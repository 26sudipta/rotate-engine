import { Link } from "react-router-dom";
import { Leaf } from "lucide-react";

const variants = {
  dark: { shell: "bg-forest text-white hover:bg-forest-mid", dot: "bg-sun text-forest" },
  light: { shell: "bg-white text-forest hover:bg-cream", dot: "bg-sun text-forest" },
  outline: { shell: "border border-forest/25 bg-transparent text-forest hover:border-forest hover:bg-forest/5", dot: "bg-sun text-forest" },
};

/** Pill button with the yellow circular icon from the reference design. */
export default function PillButton({
  to,
  onClick,
  children,
  variant = "dark",
  icon: Icon = Leaf,
  type = "button",
  disabled = false,
  className = "",
}) {
  const v = variants[variant];
  const classes = `group inline-flex items-center gap-3 whitespace-nowrap rounded-full py-1.5 pl-6 pr-1.5 text-[14px] font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${v.shell} ${className}`;
  const dot = (
    <span className={`flex h-9 w-9 items-center justify-center rounded-full transition-transform group-hover:rotate-12 ${v.dot}`}>
      <Icon size={16} strokeWidth={2.2} />
    </span>
  );

  if (to) {
    return (
      <Link to={to} className={classes}>
        {children}
        {dot}
      </Link>
    );
  }
  return (
    <button type={type} onClick={onClick} disabled={disabled} className={classes}>
      {children}
      {dot}
    </button>
  );
}
