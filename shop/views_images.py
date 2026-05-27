def default_image(request):
    """Retourne une image SVG par défaut en base64"""
    from django.http import HttpResponse

    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="300" height="300">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#a855f7;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="300" height="300" fill="url(#grad1)"/>
  <g opacity="0.3" transform="translate(150, 150)">
    <circle cx="0" cy="-50" r="50" fill="#ffffff"/>
    <path d="M -70 50 L 0 0 L 70 50 Z" stroke="#ffffff" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
  <text x="150" y="280" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#ffffff" text-anchor="middle" opacity="0.6">AUCUNE IMAGE</text>
</svg>"""
    return HttpResponse(svg_content, content_type="image/svg+xml")


def default_avatar(request):
    """Retourne un avatar SVG par défaut"""
    from django.http import HttpResponse

    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
  <defs>
    <linearGradient id="avatar_grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#06b6d4;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0891b2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="200" height="200" fill="url(#avatar_grad)"/>
  <circle cx="100" cy="70" r="40" fill="#ffffff" opacity="0.9"/>
  <path d="M 50 150 Q 50 130 100 130 Q 150 130 150 150 Q 150 180 100 180 Q 50 180 50 150" fill="#ffffff" opacity="0.8"/>
</svg>"""
    return HttpResponse(svg_content, content_type="image/svg+xml")
