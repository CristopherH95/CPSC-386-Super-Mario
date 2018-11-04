from pygame import image, time


class Animator:
    """Handles simple animations based on multiple images"""
    def __init__(self, image_list, delay=150, repeat=True):
        self.images = []
        for image_file in image_list:
            self.images.append(image.load(image_file))
        self.image_index = 0
        self.last_frame = time.get_ticks()
        self.frame_delay = delay
        self.repeat = repeat

    def reset(self):
        """Resets the animation back to its first frame"""
        self.image_index = 0

    def get_image(self):
        """Get the current image in the animation"""
        next_frame = abs(self.last_frame - time.get_ticks()) > self.frame_delay
        if next_frame and self.repeat:
            self.image_index = (self.image_index + 1) % len(self.images)
            self.last_frame = time.get_ticks()
        elif next_frame and not self.image_index >= len(self.images) - 1:
            self.image_index += 1
            self.last_frame = time.get_ticks()
        return self.images[self.image_index]
