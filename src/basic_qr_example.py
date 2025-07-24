# basic_qr_example.py

from qrstyle import QRCodeBuilder, THEMES

# Example 1: Basic black-and-white QR code
# qr1 = QRCodeBuilder(
#     data="https://github.com/yourname/qrstyle",
#     theme=THEMES["night"],  # black/white theme
#     rounded=False,
#     logo_path=None
# )
# qr_img1 = qr1.generate()
# qr_img1.show()  # or qr1.save("basic_qr.png")

# Example 2: Styled QR code with logo
qr2 = QRCodeBuilder(
    data="https://your-portfolio.com",
    theme=THEMES["night"],  # colorful theme
    rounded=True,
    logo_path="assets/logo.png"  # path to your logo image
)
qr_img2 = qr2.generate()
qr_img2.show()  
