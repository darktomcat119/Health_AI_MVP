import { redirect } from "next/navigation";

/**
 * Home page — redirects to the chat interface.
 */
export default function HomePage() {
  redirect("/chat");
}
