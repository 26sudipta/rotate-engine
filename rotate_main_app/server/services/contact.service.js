// Prototype only: messages are held in memory and are never emailed.
const messages = [];

export function validateContact({ name, email, message }) {
  const errors = [];
  if (!name?.trim()) errors.push("name is required");
  if (!/^\S+@\S+\.\S+$/.test(email ?? "")) errors.push("a valid email is required");
  if ((message ?? "").trim().length < 10) errors.push("message must be at least 10 characters");
  return errors;
}

export function saveContact({ name, email, organization = "", message }) {
  const entry = {
    id: messages.length + 1,
    name: name.trim(),
    email: email.trim(),
    organization: organization.trim(),
    message: message.trim(),
    receivedAt: new Date().toISOString(),
  };
  messages.push(entry);
  return entry;
}
