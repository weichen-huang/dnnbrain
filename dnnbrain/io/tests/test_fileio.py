import os
import h5py
import pytest
import numpy as np

from os.path import join as pjoin
from dnnbrain.io.fileio import StimulusFile, ActivationFile, MaskFile

DNNBRAIN_TEST = pjoin(os.environ['DNNBRAIN_DATA'], 'test')
TMP_DIR = pjoin(os.path.expanduser('~'), '.dnnbrain_tmp')
if not os.path.isdir(TMP_DIR):
    os.makedirs(TMP_DIR)


class TestStimulusFile:

    def test_read(self):

        # ground truth
        stim_type = 'image'
        stim_title = 'ImageNet images in all 5000scenes runs of sub-CSI1_ses-01'
        stim_id = ['n01930112_19568.JPEG', 'n03733281_29214.JPEG']
        stim_rt = [3.6309, 4.2031]

        # load by StimulusFile.read()
        stim_file = pjoin(DNNBRAIN_TEST, 'image', 'sub-CSI1_ses-01_imagenet.stim.csv')
        stim = StimulusFile(stim_file).read()

        # compare
        assert stim['type'] == stim_type
        assert stim['title'] == stim_title
        assert stim['data']['stimID'][:2].tolist() == stim_id
        assert stim['data']['RT'][:2].tolist() == stim_rt

    def test_write(self):

        # ground truth
        type = 'video'
        path = 'video_file'
        title = 'video stimuli'
        data = {'stimID': [1, 3, 5]}

        # save by StimulusFile.write()
        fname = pjoin(TMP_DIR, 'test.stim.csv')
        StimulusFile(fname).write(type, path, data, title=title)

        # compare
        stim_dict = StimulusFile(fname).read()
        assert stim_dict['type'] == type
        assert stim_dict['path'] == path
        assert stim_dict['title'] == title
        assert stim_dict['data']['stimID'].tolist() == data['stimID']


class TestActivationFile:

    def test_read(self):

        # read file
        fpath = pjoin(DNNBRAIN_TEST, "image", "sub-CSI1_ses-01_imagenet.act.h5")
        test_read = ActivationFile(fpath).read()
        rf = h5py.File(fpath, 'r')

        # assert
        assert np.all(test_read['conv5']['raw_shape'] == rf['conv5'].attrs['raw_shape'])
        assert np.all(test_read['conv5']['data'] == np.array(rf['conv5']))
        assert np.all(test_read['fc3']['raw_shape'] == rf['fc3'].attrs['raw_shape'])
        assert np.all(test_read['fc3']['data'] == np.array(rf['fc3']))
        rf.close()

    def test_write(self):

        # prepare dictionary
        fpath = pjoin(TMP_DIR, 'test.act.h5')
        act = np.random.randn(2, 3)
        raw_shape = act.shape
        layers = ['conv4', 'fc2']
        act_dict = {layers[0]: {'data': act, 'raw_shape': raw_shape},
                    layers[1]: {'data': act, 'raw_shape': raw_shape}}

        # write
        ActivationFile(fpath).write(act_dict)

        # compare
        rf = ActivationFile(fpath).read()
        assert np.all(rf[layers[0]]['data'] == np.array(act))
        assert np.all(rf[layers[0]]['raw_shape'] == np.array(raw_shape))


class TestMaskFile:

    def test_read(self):

        # ground truth
        conv5_chn = [1, 2, 3]
        conv5_row = [4, 5]
        conv5_col = [6, 7, 8]
        fc3_chn = [1, 2, 3]
        fc3_keys = ['chn']

        # load by MaskFile.read()
        fname = pjoin(DNNBRAIN_TEST, 'alexnet.dmask.csv')
        dmask = MaskFile(fname).read()

        # assert
        assert dmask['conv5']['chn'] == conv5_chn
        assert dmask['conv5']['row'] == conv5_row
        assert dmask['conv5']['col'] == conv5_col
        assert dmask['fc3']['chn'] == fc3_chn
        assert list(dmask['fc3'].keys()) == fc3_keys

    def test_write(self):

        # ground truth
        dmask1 = {
            'conv1': {'col': [1, 2, 3]},
            'conv2': {'row': [2, 5, 6]},
            'fc1': {'chn': [2, 4, 6]}
        }

        # save by MaskFile.write()
        fname = pjoin(TMP_DIR, 'test.dmask.csv')
        MaskFile(fname).write(dmask1)

        # assert
        dmask2 = MaskFile(fname).read()
        assert dmask1.keys() == dmask2.keys()
        assert dmask1['conv1']['col'] == dmask2['conv1']['col']
        assert dmask1['conv2']['row'] == dmask2['conv2']['row']
        assert dmask1['fc1']['chn'] == dmask2['fc1']['chn']
        assert dmask1['fc1'].keys() == dmask2['fc1'].keys()


if __name__ == '__main__':
    pytest.main()
