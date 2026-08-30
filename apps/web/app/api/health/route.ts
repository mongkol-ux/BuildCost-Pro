import { NextResponse } from "next/server";

export function GET() {
  return NextResponse.json({ status: "ok", service: "buildcost-pro-web", version: "1.1.0" });
}
