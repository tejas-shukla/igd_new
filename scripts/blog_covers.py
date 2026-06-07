"""
SVG cover art generator for IGotDomain blog articles.
Matches the branded illustrations already deployed on the site.
"""
 
def generate_cover(motif_key: str, variant: int = 0) -> str:
    """
    Returns an inline SVG string for the given topic motif.
    variant 0=teal, 1=deep-teal, 2=mint — subtle gradient variety.
    """
    grads = [
        ("#14B8A6", "#0D9488", "#0F766E"),   # teal
        ("#0D9488", "#0F766E", "#134E4A"),   # deep
        ("#5EEAD4", "#14B8A6", "#0D9488"),   # mint
    ]
    g1, g2, g3 = grads[variant % 3]
    uid = abs(hash(motif_key + str(variant))) % 9999
 
    MOTIFS = {
        'domain': '''<circle cx="0" cy="0" r="62" opacity="0.95"/>
            <ellipse cx="0" cy="0" rx="26" ry="62"/>
            <line x1="-62" y1="0" x2="62" y2="0"/>
            <path d="M-54 -30 H54 M-54 30 H54" opacity="0.85"/>''',
 
        'checklist': '''<rect x="-58" y="-66" width="116" height="132" rx="12" opacity="0.95"/>
            <path d="M-38 -34 l10 10 l20 -22" stroke-width="6"/>
            <line x1="6" y1="-28" x2="40" y2="-28"/>
            <path d="M-38 6 l10 10 l20 -22" stroke-width="6"/>
            <line x1="6" y1="0" x2="40" y2="0"/>
            <line x1="-38" y1="40" x2="40" y2="40" opacity="0.6"/>''',
 
        'ai': '''<path d="M0 -68 L16 -16 L68 0 L16 16 L0 68 L-16 16 L-68 0 L-16 -16 Z" opacity="0.95"/>
            <circle cx="0" cy="0" r="10" fill="#ffffff" stroke="none"/>
            <circle cx="52" cy="-48" r="6" fill="#ffffff" stroke="none" opacity="0.8"/>
            <circle cx="-56" cy="44" r="5" fill="#ffffff" stroke="none" opacity="0.7"/>''',
 
        'validate': '''<circle cx="-8" cy="-14" r="40"/>
            <path d="M-22 22 h28 M-18 34 h20"/>
            <line x1="-8" y1="-14" x2="-8" y2="6" opacity="0.6"/>
            <circle cx="44" cy="40" r="22"/>
            <line x1="60" y1="56" x2="78" y2="74" stroke-width="8"/>''',
 
        'website': '''<rect x="-66" y="-54" width="132" height="108" rx="12" opacity="0.95"/>
            <line x1="-66" y1="-26" x2="66" y2="-26"/>
            <circle cx="-50" cy="-40" r="4" fill="#ffffff" stroke="none"/>
            <circle cx="-36" cy="-40" r="4" fill="#ffffff" stroke="none"/>
            <circle cx="-22" cy="-40" r="4" fill="#ffffff" stroke="none"/>
            <rect x="-50" y="-12" width="40" height="50" rx="6" opacity="0.7"/>
            <line x1="2" y1="-8" x2="50" y2="-8"/>
            <line x1="2" y1="10" x2="50" y2="10"/>
            <line x1="2" y1="28" x2="34" y2="28" opacity="0.6"/>''',
 
        'growth': '''<polyline points="-66,46 -22,2 12,30 64,-44"/>
            <polyline points="38,-44 64,-44 64,-18"/>
            <line x1="-66" y1="60" x2="66" y2="60" opacity="0.5"/>''',
 
        'marketing': '''<path d="M-58 -14 L26 -44 L26 44 L-58 14 Z" opacity="0.95"/>
            <path d="M-58 -14 L-58 14 L-30 22 L-30 -22 Z" fill="#ffffff" stroke="none" opacity="0.85"/>
            <path d="M44 -26 q22 26 0 52" stroke-width="6"/>
            <path d="M58 -44 q40 44 0 88" stroke-width="6" opacity="0.7"/>''',
 
        'pricing': '''<path d="M-50 -50 L8 -50 L62 4 L8 58 L-50 0 Z" opacity="0.95"/>
            <circle cx="-26" cy="-24" r="9" fill="#ffffff" stroke="none"/>
            <line x1="-2" y1="-8" x2="34" y2="28" opacity="0.7"/>''',
 
        'banking': '''<rect x="-68" y="-44" width="136" height="88" rx="12" opacity="0.95"/>
            <line x1="-68" y1="-18" x2="68" y2="-18"/>
            <rect x="-54" y="8" width="30" height="20" rx="4" opacity="0.7"/>
            <line x1="14" y1="20" x2="52" y2="20" opacity="0.6"/>''',
    }
 
    motif = MOTIFS.get(motif_key, MOTIFS['domain'])
    dots = ''.join(
        f'<circle cx="{40+(i%8)*72}" cy="{40+(i//8)*70}" r="3"/>'
        for i in range(40)
    )
 
    return f'''<svg viewBox="0 0 600 360" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;display:block">
<defs>
<linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{g1}"/><stop offset="0.55" stop-color="{g2}"/><stop offset="1" stop-color="{g3}"/>
</linearGradient>
<radialGradient id="glow{uid}" cx="0.7" cy="0.25" r="0.8">
  <stop offset="0" stop-color="#ffffff" stop-opacity="0.28"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
</radialGradient>
</defs>
<rect width="600" height="360" fill="url(#bg{uid})"/>
<rect width="600" height="360" fill="url(#glow{uid})"/>
<g fill="#ffffff" opacity="0.10">{dots}</g>
<circle cx="510" cy="70" r="60" fill="#ffffff" opacity="0.07"/>
<circle cx="70" cy="300" r="48" fill="#ffffff" opacity="0.06"/>
<g transform="translate(300 180)" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round">
{motif}
</g>
</svg>'''
 
 
# Topic → (motif_key, variant) mapping for the weekly agent
TOPIC_MOTIFS = {
    'domains':         ('domain',    0),
    'website-builders':('website',   1),
    'banking':         ('banking',   1),
    'accounting':      ('checklist', 2),
    'payments':        ('pricing',   0),
    'ai-tools':        ('ai',        2),
    'startup-strategy':('validate',  2),
    'marketing':       ('marketing', 2),
    'email':           ('checklist', 0),
    'crm':             ('growth',    0),
}
 
if __name__ == '__main__':
    # Quick test
    svg = generate_cover('banking', 1)
    assert '<svg' in svg and '</svg>' in svg
    print(f"OK — generated {len(svg)} char SVG")
    for key in ['domain','checklist','ai','validate','website','growth','marketing','pricing','banking']:
        svg = generate_cover(key)
        assert len(svg) > 100
        print(f"  ✓ {key}")
