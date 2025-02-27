# khw 2024.1.20 updated #
# usage > python lk_track_save_data.py  video_filename
# or
# usage > python lk_track_save_data.py 0 #grab from camera 0 (default laptop webcam )
#
# filename: lk_track_save_data.py (reference only), this program tracks and saves features into a file test_sample.txt
# modified from sample code : https://github.com/opencv/opencv  \opencv-4.x\opencv-4.x\samples\python
# Download the whole set of samples, save this code in \opencv-4.x\opencv-4.x\samples\python\ and run it.
#!/usr/bin/env python


'''
Lucas-Kanade tracker
====================

Lucas-Kanade sparse optical flow demo. Uses goodFeaturesToTrack
for track initialization and back-tracking for match verification
between frames.

Usage
-----
lk_track.py [<video_source>]


Keys
----
ESC - exit
'''

# Python 2/3 compatibility
from __future__ import print_function

import numpy as np
import cv2 as cv

import video
from common import anorm2, draw_str

lk_params = dict(winSize=(15, 15),
                 maxLevel=2,
                 criteria=(cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict(maxCorners=500,
                      qualityLevel=0.3,
                      minDistance=7,
                      blockSize=7)


class App:
    def __init__(self, video_src):
        self.track_len = 10
        self.detect_interval = 5
        self.tracks = []
        self.cam = video.create_capture(video_src)
        self.frame_idx = 0

    def run(self):
        f = open("lk_output.txt", "w")  # khw
        while True:
            _ret, frame = self.cam.read()
            if _ret != True:  # khw , this is to avoid the error message at the end of file read
                f.close()  # khw
                break  # khw
            frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            vis = frame.copy()

            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1]
                                for tr in self.tracks]).reshape(-1, 1, 2)
                p1, _st, _err = cv.calcOpticalFlowPyrLK(
                    img0, img1, p0, None, **lk_params)
                p0r, _st, _err = cv.calcOpticalFlowPyrLK(
                    img1, img0, p1, None, **lk_params)
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                good = d < 1
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                    cv.circle(vis, (int(x), int(y)), 2, (0, 255, 0), -1)
                    f.write(str(x))  # khw
                    f.write(",")  # khw
                    f.write(str(y))  # khw
                    f.write("\n")  # khw
                f.write("-----  end of a time stamp ----")  # khw
                f.write("\n")  # khw

                self.tracks = new_tracks
                cv.polylines(vis, [np.int32(tr)
                             for tr in self.tracks], False, (0, 255, 0))
                draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))

            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv.circle(mask, (x, y), 5, 0, -1)
                p = cv.goodFeaturesToTrack(
                    frame_gray, mask=mask, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])
                        # #print(x) #khw
                        # #print(y)  #khw
                        # f.write(str(x))
                        # f.write(",")
                        # f.write(str(y))
                        # f.write("\n")
                # f.write("end of a time stamp") #khw
                # f.write("\n")  #khw

            self.frame_idx += 1
            self.prev_gray = frame_gray
            cv.imshow('lk_track', vis)
            # f.write(str(vis))

            ch = cv.waitKey(1)
            if ch == 27:
                f.close()  # khw
                break


def main():
    import sys
    try:
        video_src = sys.argv[1]
    except:
        video_src = 0
    App(video_src).run()
    print('Done')


if __name__ == '__main__':
    print(__doc__)
    main()
    cv.destroyAllWindows()
