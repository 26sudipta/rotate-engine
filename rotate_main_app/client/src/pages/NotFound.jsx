import PillButton from "../components/ui/PillButton.jsx";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-[600px] px-6 py-24 text-center">
      <p className="font-script text-[90px] leading-none text-sun-deep">404</p>
      <h2 className="mt-2 font-display text-[26px] font-bold">This field hasn't been planted yet.</h2>
      <p className="mt-3 text-ink-soft">The page you're looking for doesn't exist. Head back to the dashboard.</p>
      <div className="mt-8 flex justify-center"><PillButton to="/dashboard">Go to Dashboard</PillButton></div>
    </div>
  );
}
