import torch
import torch.nn.functional as F
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class RNNEncoder(nn.Module):

    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int = 1,
        bidirectional=True,
        rnn=nn.LSTM,
        dropout=0
    ):
        super().__init__()

        self.num_directions = 2 if bidirectional else 1

        self.rnn: nn.LSTM = rnn(
            input_size,
            hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=dropout
        )

    def forward(self, input, lengths):
        sorted_input, sorted_lengths, reverse_indices = self._sort_batch(
            input, lengths)

        packed_input = pack_padded_sequence(
            sorted_input, sorted_lengths.cpu(), batch_first=True)

        self.rnn.flatten_parameters()
        output, hidden = self.rnn(packed_input)

        output, lengths = pad_packed_sequence(output, batch_first=True)

        output = output[reverse_indices]

        if isinstance(self.rnn, nn.LSTM):
            hidden = hidden[0]

        hidden = hidden[-self.num_directions:]
        hidden = hidden.transpose(0, 1).contiguous()
        hidden = hidden.view(hidden.size(0), -1)
        hidden = hidden[reverse_indices]

        return output, hidden

    def _sort_batch(self, input: torch.Tensor, lengths: torch.Tensor):
        sorted_legnths, indices = lengths.sort(dim=0, descending=True)
        sorted_input = input[indices]

        reverse_indices = indices.scatter(
            0, indices, torch.arange(len(indices), device=lengths.device)
        )

        return sorted_input, sorted_legnths, reverse_indices


class RNNEncoderOld(nn.Module):
    """A RNN wrapper handles variable length inputs, always set batch_first=True.
    Supports LSTM, GRU and RNN. Tested with PyTorch 0.3 and 0.4
    """

    def __init__(self, word_embedding_size, hidden_size, bidirectional=True,
                 dropout_p=0, n_layers=1, rnn_type="lstm", return_hidden=True, return_outputs=True):
        super(RNNEncoderOld, self).__init__()
        """  
        :param word_embedding_size: rnn input size
        :param hidden_size: rnn output size
        :param dropout_p: between rnn layers, only useful when n_layer >= 2
        """
        self.rnn_type = rnn_type
        self.n_dirs = 2 if bidirectional else 1
        # - add return_hidden keyword arg to reduce computation if hidden is not needed.
        self.return_hidden = return_hidden
        self.return_outputs = return_outputs
        self.rnn = getattr(nn, rnn_type.upper())(word_embedding_size, hidden_size, n_layers,
                                                 batch_first=True,
                                                 bidirectional=bidirectional,
                                                 dropout=dropout_p)

    def sort_batch(self, seq, lengths):
        sorted_lengths, perm_idx = lengths.sort(0, descending=True)
        reverse_indices = [0] * len(perm_idx)
        for i in range(len(perm_idx)):
            reverse_indices[perm_idx[i]] = i
        sorted_seq = seq[perm_idx]
        return sorted_seq, list(sorted_lengths), reverse_indices

    def forward(self, inputs, lengths):
        """
        inputs, sorted_inputs -> (B, T, D)
        lengths -> (B, )
        outputs -> (B, T, n_dirs * D)
        hidden -> (n_layers * n_dirs, B, D) -> (B, n_dirs * D)  keep the last layer
        - add total_length in pad_packed_sequence for compatiblity with nn.DataParallel, --remove it
        """
        assert len(inputs) == len(lengths)
        sorted_inputs, sorted_lengths, reverse_indices = self.sort_batch(
            inputs, lengths)
        packed_inputs = pack_padded_sequence(
            sorted_inputs, sorted_lengths, batch_first=True)
        outputs, hidden = self.rnn(packed_inputs)
        if self.return_outputs:
            # outputs, lengths = pad_packed_sequence(outputs, batch_first=True, total_length=int(max(lengths)))
            outputs, lengths = pad_packed_sequence(outputs, batch_first=True)
            outputs = outputs[reverse_indices]
        else:
            outputs = None
        if self.return_hidden:  #
            if self.rnn_type.lower() == "lstm":
                hidden = hidden[0]
            hidden = hidden[-self.n_dirs:, :, :]
            hidden = hidden.transpose(0, 1).contiguous()
            hidden = hidden.view(hidden.size(0), -1)
            hidden = hidden[reverse_indices]
        else:
            hidden = None
        return outputs, hidden


def max_along_time(outputs, lengths):
    """ Get maximum responses from RNN outputs along time axis
    :param outputs: (B, T, D)
    :param lengths: (B, )
    :return: (B, D)
    """
    outputs = [outputs[i, :int(lengths[i]), :].max(dim=0)[0]
               for i in range(len(lengths))]

    return torch.stack(outputs, dim=0)
