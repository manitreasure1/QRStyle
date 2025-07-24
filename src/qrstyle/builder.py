import io
from typing import Optional
from PIL import Image, ImageDraw, ImageOps
import segno


class QRCodeBuilder:
    def __init__(
        self,
        data: str,
        scale: int = 5,
        theme: Optional[dict] = None,
        logo_path: Optional[str] = None,
        rounded: bool = False,
    ):
        if not data:
            raise ValueError("QR data cannot be empty.")

        self.data = data
        self.scale = scale
        self.theme = theme or {"dark": "black", "light": "white"}
        self.logo_path = logo_path
        self.rounded = rounded

    def generate(self) -> Image.Image:
        qr = segno.make(self.data, error='H')

        # Generate QR image
        buf = io.BytesIO()
        qr.save(
            out=buf,
            kind="png",
            scale=self.scale,
            dark=self.theme["dark"],
            light=self.theme["light"],
            border=1,
        )
        buf.seek(0)
        qr_img = Image.open(buf).convert("RGBA")

        # Add logo if applicable
        if self.logo_path:
            qr_img = self._embed_logo(qr_img)

        return qr_img

    def _embed_logo(self, qr_img: Image.Image) -> Image.Image:
        if not self.logo_path:
            raise ValueError("Logo path must be provided to embed a logo.")
        logo = Image.open(self.logo_path).convert("RGBA")
        qr_width, qr_height = qr_img.size
        logo_size = min(qr_width, qr_height) // 4
        logo = logo.resize((logo_size, logo_size), resample=Image.Resampling.LANCZOS)

        # Step 1: Convert to grayscale if it's a colored image
        if self._is_colored(logo):
            logo = self._recolor_logo(logo, self.theme["dark"], self.theme["light"])

        # Step 2: Make it round if requested
        if self.rounded:
            mask = Image.new("L", (logo_size, logo_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, logo_size, logo_size), fill=255)

            rounded_logo = Image.new("RGBA", (logo_size, logo_size))
            rounded_logo.paste(logo, (0, 0), mask=mask)
            logo = rounded_logo

        # Step 3: Paste onto center
        pos = (
            (qr_width - logo_size) // 2,
            (qr_height - logo_size) // 2,
        )
        qr_img.paste(logo, pos, mask=logo)
        return qr_img

    def _is_colored(self, img: Image.Image) -> bool:
        """
        Returns True if the image has more than one unique color tone.
        """
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        grayscale = img.convert("L")
        extrema = grayscale.getextrema()
        return extrema[0] != extrema[1]

    def _recolor_logo(self, logo: Image.Image, dark_color: str, light_color: str) -> Image.Image:
        """
        Converts a logo image to a single dark color with transparent light areas.
        """
        # Convert to grayscale then to alpha mask
        gray = ImageOps.grayscale(logo)
        bw = ImageOps.invert(gray).point(lambda x: 255 if x > 10 else 0, mode='1')  # threshold

        # Create a new image filled with dark color
        colored_logo = Image.new("RGBA", logo.size, dark_color)
        mask = bw.convert("L")

        # Apply mask to dark color
        result = Image.new("RGBA", logo.size)
        result.paste(colored_logo, (0, 0), mask=mask)

        return result

    def save(self, path: str):
        img = self.generate()
        img.save(path)
