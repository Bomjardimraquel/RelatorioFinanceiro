export function LedraIcon({ variant = "dark", size = 32 }) {
  const bars = variant === "light" ? "#FFFFFF" : "#0C2340";
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 125 130" width={size} height={size}>
      <polygon points="10,80 28,62 28,115 10,115" fill={bars} />
      <polygon points="36,54 54,36 54,115 36,115" fill={bars} />
      <polygon points="62,28 80,10 80,87 62,105" fill="#C9A84C" />
      <polygon points="80,97 115,97 115,115 62,115" fill="#C9A84C" />
    </svg>
  );
}