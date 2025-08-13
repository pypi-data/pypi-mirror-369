from threading import Lock
from time import time
import numpy as np
from pathlib import Path
from PIL import Image
import logging

from .common_render_widget import CommonRenderWidget


class AnimatedRenderWidget(CommonRenderWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.playing_animation = False
        self._animation_lock = Lock()
        self._animation_frame = 0
        self._animation_last_time = 0
        self._animation_total_frames = 30
        self._animation_fps = 30
        self._animation_cycles = 0
        self._animation_current_cycle = 0
        self._animation_timer = self.render_interactor.CreateRepeatingTimer(500)
        self.render_interactor.AddObserver("TimerEvent", self._animation_callback)

    def start_animation(self, fps=None, frames=None, cycles=None):
        if isinstance(fps, int | float):
            self._animation_fps = fps

        if isinstance(frames, int):
            self._animation_total_frames = frames

        if isinstance(cycles, int):
            self._animation_cycles = cycles
            self._animation_current_cycle = 0
        else:
            self._animation_cycles = 0
            self._animation_current_cycle = 0

        if self.playing_animation:
            return

        self.playing_animation = True

    def stop_animation(self):
        if not self.playing_animation:
            return

        if self._animation_timer is None:
            return

        self.playing_animation = False

    def toggle_animation(self):
        if self.playing_animation:
            self.stop_animation()
        else:
            self.start_animation()

    def _animation_callback(self, obj, event):
        """
        Common function with controls that are meaningfull to
        all kinds of animations.
        """

        if not self.playing_animation:
            return

        # Wait the rendering of the last frame
        # before starting a new one
        if self._animation_lock.locked():
            return

        # Only needed because vtk CreateRepeatingTimer(n)
        # does not work =/
        dt = time() - self._animation_last_time
        if (dt) < 1 / self._animation_fps:
            return

        if (self._animation_cycles != 0) and (self._animation_current_cycle >= self._animation_cycles):
            self.stop_animation()
            return

        if self._animation_frame == 0:
            self._animation_current_cycle += 1

        with self._animation_lock:
            self._animation_frame = (
                self._animation_frame + 1
            ) % self._animation_total_frames
            self.update_animation(self._animation_frame)
            self._animation_last_time = time()

    def update_animation(self, frame: int):
        raise NotImplementedError(
            'The function "update_animation" was not implemented!'
        )

    def save_video(self, path: str | Path, n_loops=20):
        '''
        Saves a video of multiple cycles of the current animation.
        Supported formats are MP4, AVI, OGV, and WEBM.
        '''
        from moviepy.editor import ImageSequenceClip

        # Stop animation to prevent conflicts
        previous_state = self.playing_animation
        self.stop_animation()

        logging.info("Generating video frames...")
        images = list()
        for i in range(self._animation_total_frames):
            self.update_animation(i)
            screenshot = self.get_screenshot().resize([1920, 1080])
            images.append(screenshot)
        frames = [np.array(img) for img in images]

        # recover the playing animation status
        self.playing_animation = previous_state
        
        logging.info("Saving video to file...")
        clip = ImageSequenceClip(frames, self._animation_fps)
        clip = clip.loop(duration = clip.duration * n_loops)
        clip.write_videofile(str(path), preset="veryfast", logger=None)

    def save_animation(self, path: str | Path):
        '''
        Saves an animated image file of a animation cycle.
        Supported formats are WEBP and GIF.

        We strongly recomend you to use webp, because of the reduced
        file size and the superior visual quality.
        Despite that, gifs are usefull sometimes because of its popularity.
        '''

        path = Path(path)
        is_gif = path.suffix == ".gif"

        # Stop animation to prevent conflicts
        previous_state = self.playing_animation
        self.stop_animation()

        logging.info("Generating animation frames...")
        images:list[Image.Image] = list()
        for i in range(self._animation_total_frames):
            self.update_animation(i)
            screenshot = self.get_screenshot().convert("RGB").resize([1280, 720])
            if is_gif:
                screenshot = screenshot.quantize(method=Image.Quantize.FASTOCTREE, kmeans=2)
            images.append(screenshot)

        # recover the playing animation status
        self.playing_animation = previous_state

        logging.info("Saving animation to file...")
        images[0].save(
            path,
            save_all=True,
            append_images=images[1:],
            duration=self._animation_total_frames / self._animation_fps,
            loop=0,
            optimize=True,
            lossless=True,
        )
