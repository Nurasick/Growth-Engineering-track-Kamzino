import fs from "fs";
import path from "path";
import { unstable_noStore as noStore } from "next/cache";
import { PlaybooksClient } from "./PlaybooksClient";

export const dynamic = "force-dynamic";

function readMd(filename: string): string {
  try {
    const root = path.resolve(process.cwd(), "..");
    return fs.readFileSync(path.join(root, filename), "utf-8");
  } catch {
    return `# Error\n\nCould not load \`${filename}\`.`;
  }
}

export default function PlaybooksPage() {
  noStore();
  const analysis = readMd("PLAYBOOK_ANALYSIS_GENERATED.md");
  const counter = readMd("COUNTER_PLAYBOOK.md");

  return <PlaybooksClient analysis={analysis} counter={counter} />;
}
