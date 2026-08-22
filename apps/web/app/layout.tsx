import "./globals.css";

export const metadata = {
  title: "BuildCost Pro",
  description: "Construction cost and project management platform",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
