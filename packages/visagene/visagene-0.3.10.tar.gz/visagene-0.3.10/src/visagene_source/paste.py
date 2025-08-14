import cupy as cp
import pixtreme as px


class PasteBack:
    def __init__(self, blursize: float = 1.0):
        self.gaussian_blur = px.GaussianBlur()
        self.blursize = blursize
        self.mask = None
        self.size = None

    def create_mask(self, size: tuple):
        padding_v = int(size[0] // 5 * self.blursize)
        padding_h = int(size[1] // 7 * self.blursize)

        white_plate = cp.ones((size[0], size[1], 3), dtype=cp.float32)
        white_plate[:padding_v, :] = 0
        white_plate[-padding_v:, :] = 0
        white_plate[:, :padding_h] = 0
        white_plate[:, -padding_h:] = 0
        return self.gaussian_blur.get(white_plate, int(padding_h), float(padding_h))

    def get(
        self,
        target_image: cp.ndarray,
        paste_image: cp.ndarray,
        M: cp.ndarray,
    ) -> cp.ndarray:
        target_image = px.to_float32(target_image)
        paste_image = px.to_float32(paste_image)

        if self.size != paste_image.shape[:2]:
            self.size = paste_image.shape[:2]
            self.mask = self.create_mask(self.size)

        merged_image = paste_back(target_image, paste_image, M, self.mask)

        return merged_image


def paste_back(
    target_image: cp.ndarray,
    paste_image: cp.ndarray,
    M: cp.ndarray,
    mask: cp.ndarray = None,
) -> cp.ndarray:
    if mask is None:
        mask = cp.ones((paste_image.shape[0], paste_image.shape[1], 3), dtype=cp.float32)
    else:
        mask = px.resize(mask, (paste_image.shape[1], paste_image.shape[0]), interpolation=px.INTER_AUTO)

    IM = px.get_inverse_matrix(M)
    paste_image = px.affine_transform(paste_image, IM, (target_image.shape[0], target_image.shape[1]))
    paste_mask = px.affine_transform(mask, IM, (target_image.shape[0], target_image.shape[1]))
    merged_image = paste_mask * paste_image + (1 - paste_mask) * target_image
    return merged_image
