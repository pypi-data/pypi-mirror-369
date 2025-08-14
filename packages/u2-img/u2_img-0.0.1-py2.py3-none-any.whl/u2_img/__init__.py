import os
import time
import tempfile
from imgUtil import ImageUtil
from comparison import isMatch, getMatchedCenterOffset
from uiautomator2 import Device



def img_tz(d: Device):

    class _Img(object):
        def exists(self, query, origin=None, interval=2, timeout=4, algorithm='sift', threshold=0.75, colormode=0):
            if origin:
                try:
                    pos = ImageUtil.find_image_positon(query, origin, algorithm, threshold, colormode)
                    if pos:
                        return True
                except:
                    pass
                return False
            begin = time.time()
            isExists = False
            src_img_path = tempfile.mktemp()
            d.screenshot(src_img_path)
            while (time.time() - begin < timeout):
                time.sleep(interval)
                d.screenshot(src_img_path)
                try:
                    pos = ImageUtil.find_image_positon(query, src_img_path, algorithm, threshold, colormode)
                    if pos:
                        isExists = True
                except:
                    pass
                if not isExists:
                    time.sleep(interval)
                    del_file(src_img_path)
                    continue
                del_file(src_img_path)
                return isExists

        def click(self, query, origin=None, algorithm='sift', threshold=0.75, colormode=0):
            pos = self.get_location(query, origin, algorithm, threshold, colormode)
            if pos:
                d.click(pos[0], pos[1])
            else:
                raise AssertionError("not find sub img on big img")

        def get_location(self, query, origin=None, algorithm='sift', threshold=0.75, colormode=0):
            src_img_path = origin
            if src_img_path is None:
                src_img_path = tempfile.mktemp() + ".png"
                d.screenshot(src_img_path)
            if not os.path.exists(src_img_path):
                raise IOError('path not origin img')
            try:
                pos = ImageUtil.find_image_positon(query, src_img_path, algorithm, threshold, colormode)
                return pos
            except:
                raise
            finally:
                if origin is None:
                    del_file(src_img_path)

    return _Img()



def img(d: Device):

    class _Img(object):
        def exists(self, query, origin=None, interval=2, timeout=4, threshold=0.99, colormode=0):
            threshold = 1 - threshold
            if origin:
                return isMatch(query, origin, threshold, colormode)
            begin = time.time()
            isExists = False
            tmp = tempfile.mktemp()
            while (time.time() - begin < timeout):
                d.screenshot(tmp)
                isExists = isMatch(query, tmp, threshold, colormode)
                if not isExists:
                    time.sleep(interval)
                    del_file(tmp)
                    continue
                del_file(tmp)
                return isExists

        def click(self, query, origin=None, threshold=0.99, rotation=0, colormode=0):
            threshold = 1 - threshold
            pos = self.get_location(query, origin, threshold, rotation, colormode)
            if pos:
                d.click(pos[0], pos[1])
            else:
                raise AssertionError("not find sub img on big img")

        def get_location(self, query, origin=None, threshold=0.99, rotation=0, colormode=0):
            threshold = 1 - threshold
            src_img_path = origin
            if src_img_path is None:
                src_img_path = tempfile.mktemp() +  ".png"
                d.screenshot(src_img_path)
            if not os.path.exists(src_img_path):
                raise IOError('path not origin img')
            try:
                pos = getMatchedCenterOffset(query, src_img_path, threshold, rotation, colormode)
                return pos
            except:
                raise
            finally:
                if origin is None:
                    del_file(src_img_path)

    return _Img()


def del_file(path):
    if os.path.exists(path):
        os.remove(path)
