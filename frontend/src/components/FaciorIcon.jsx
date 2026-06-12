export function FaciorIcon({ size = 32 }) {
  const scale = size / 58;
  const w = Math.round(125 * scale);
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 125 58" width={w} height={size}>
      <polygon points="5,5 55,5 67,17 5,17" fill="#0C2340" />
      <polygon points="5,23 70,23 82,35 5,35" fill="#0C2340" />
      <polygon points="5,41 55,41 67,53 5,53" fill="#0C2340" />
      <polygon points="77,5 107,29 77,53 90,53 120,29 90,5" fill="#C9A84C" />
    </svg>
  );
}

export function FaciorLogo({ height = 40 }) {
  const scale = height / 120;
  const w = Math.round(340 * scale);
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 340 120" width={w} height={height}>
      <defs>
        <style>{`
          .brand-text {
            font-family: 'Plus Jakarta Sans', 'Inter', 'Montserrat', 'Segoe UI', sans-serif;
            font-weight: 700;
            fill: #0C2340;
          }
          .tagline-text {
            font-family: 'Plus Jakarta Sans', 'Inter', 'Segoe UI', sans-serif;
            font-weight: 600;
            font-size: 11px;
            letter-spacing: 2px;
            fill: #5A6E85;
          }
        `}</style>
      </defs>
      <g>
        <polygon points="20,38 70,38 82,50 20,50" fill="#0C2340" />
        <polygon points="20,56 85,56 97,68 20,68" fill="#0C2340" />
        <polygon points="20,74 70,74 82,86 20,86" fill="#0C2340" />
        <polygon points="92,38 122,62 92,86 105,86 135,62 105,38" fill="#C9A84C" />
      </g>
      <g>
        <text x="150" y="68" fontSize="40px" className="brand-text">Facior</text>
        <text x="153" y="88" className="tagline-text">EFICIÊNCIA EM RELATÓRIOS</text>
      </g>
    </svg>
  );
}
