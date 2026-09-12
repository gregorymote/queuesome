import numpy as np

from django.test import SimpleTestCase

from utils.spotify_background_color import SpotifyBackgroundColor


class ImageProcessingCompatibilityTests(SimpleTestCase):
    def test_album_art_can_be_resized_with_pillow(self):
        image = np.zeros((4, 4, 3), dtype=np.uint8)

        processor = SpotifyBackgroundColor(
            image,
            image_processing_size=(2, 2),
        )

        self.assertEqual(processor.img.shape, (2, 2, 3))
