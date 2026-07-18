from django import template

register = template.Library()


@register.filter
def optimized(url, width=800):
    """Insert Cloudinary on-the-fly transformation params into an image URL.

    Turns https://res.cloudinary.com/.../image/upload/v123/folder/file.jpg
    into  .../image/upload/f_auto,q_auto,c_limit,w_<width>/v123/folder/file.jpg
    Falls back to the original URL when it isn't a Cloudinary upload URL.
    """
    if not url:
        return url
    transform = f"f_auto,q_auto,c_limit,w_{width}"
    return url.replace("/upload/", f"/upload/{transform}/", 1)
