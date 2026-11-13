import { useState } from "react";
import { CheckCircle2, Info, Send } from "lucide-react";
import PillButton from "../components/ui/PillButton.jsx";
import { api } from "../services/api.js";

const empty = { name: "", email: "", organization: "", message: "" };

function validate(f) {
  const e = {};
  if (!f.name.trim()) e.name = "Please enter your name.";
  if (!/^\S+@\S+\.\S+$/.test(f.email)) e.email = "Please enter a valid email address.";
  if (f.message.trim().length < 10) e.message = "Message should be at least 10 characters.";
  return e;
}

export default function Contact() {
  const [form, setForm] = useState(empty);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState("idle"); // idle | sending | sent | error
  const [serverError, setServerError] = useState("");

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    const found = validate(form);
    setErrors(found);
    if (Object.keys(found).length) return;
    setStatus("sending");
    try {
      await api.sendContact(form);
      setStatus("sent");
      setForm(empty);
    } catch (err) {
      setServerError(err.message);
      setStatus("error");
    }
  };

  const field = (k, label, props = {}) => (
    <label className="block">
      <span className="text-[13.5px] font-semibold text-ink">{label}</span>
      {props.rows ? (
        <textarea rows={props.rows} value={form[k]} onChange={set(k)} className="mt-1.5 w-full rounded-2xl border border-border bg-white px-4 py-3 text-[14.5px] focus:border-forest focus:outline-none focus:ring-2 focus:ring-forest/20" />
      ) : (
        <input type={props.type || "text"} value={form[k]} onChange={set(k)} className="mt-1.5 w-full rounded-full border border-border bg-white px-5 py-3 text-[14.5px] focus:border-forest focus:outline-none focus:ring-2 focus:ring-forest/20" />
      )}
      {errors[k] && <span className="mt-1 block text-[12.5px] text-alert">{errors[k]}</span>}
    </label>
  );

  return (
    <div className="mx-auto grid max-w-[1100px] gap-10 px-6 py-14 lg:grid-cols-[1.4fr_0.8fr]">
      <div className="card-dashed rounded-[28px] bg-cream p-8 md:p-10">
        {status === "sent" ? (
          <div className="py-10 text-center">
            <CheckCircle2 size={48} className="mx-auto text-leaf" />
            <h2 className="mt-4 font-display text-[24px] font-bold">Message received</h2>
            <p className="mx-auto mt-2 max-w-sm text-[14.5px] text-ink-soft">Thanks for getting in touch. In this prototype messages are stored on the server only for demonstration.</p>
            <div className="mt-6"><PillButton onClick={() => setStatus("idle")} variant="outline" icon={Send}>Send another</PillButton></div>
          </div>
        ) : (
          <form onSubmit={submit} noValidate className="space-y-5">
            <h2 className="font-display text-[24px] font-bold">Send us a message</h2>
            <div className="grid gap-5 sm:grid-cols-2">{field("name", "Name")}{field("email", "Email", { type: "email" })}</div>
            {field("organization", "Organization (optional)")}
            {field("message", "Message", { rows: 5 })}
            {status === "error" && <p className="text-[13.5px] text-alert">Couldn't send: {serverError}</p>}
            <PillButton type="submit" icon={Send} disabled={status === "sending"}>{status === "sending" ? "Sending..." : "Send message"}</PillButton>
          </form>
        )}
      </div>
      <aside className="space-y-5">
        <div className="rounded-[24px] bg-forest p-7 text-white">
          <div className="flex items-center gap-2 text-sun"><Info size={18} /><span className="font-script text-[24px] leading-none">About this form</span></div>
          <p className="mt-3 text-[14px] leading-relaxed text-white/85">This is a prototype. Messages are kept in the API server's memory and are not emailed or shared. Restarting the server clears them.</p>
        </div>
        <div className="rounded-[24px] border border-border p-7">
          <h3 className="font-display text-[17px] font-bold">Good things to ask about</h3>
          <ul className="mt-3 space-y-2 text-[14px] text-ink-soft">
            <li>• Connecting real NASA Earth Observation data</li>
            <li>• Validating crop-rotation indicators</li>
            <li>• Adding new districts or crops</li>
          </ul>
        </div>
      </aside>
    </div>
  );
}
