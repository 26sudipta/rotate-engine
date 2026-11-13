import { Suspense, useEffect } from "react";
import { Outlet, useLocation, matchPath } from "react-router-dom";
import Header from "./Header.jsx";
import Footer from "./Footer.jsx";
import PageBanner from "./PageBanner.jsx";
import ScrollTopButton from "./ScrollTopButton.jsx";
import LoadingState from "../LoadingState.jsx";
import { useApp } from "../../context/AppContext.jsx";

function getBanner(pathname, locationName) {
  const rules = [
    ["/dashboard", { title: "ROTATE", subtitle: "Climate-resilient crop rotation intelligence", crumbs: ["Dashboard"] }],
    ["/farm/:id", { title: "Farm Analysis", subtitle: `Selected farm analysis for ${locationName}.`, crumbs: ["Dashboard", "Farm"] }],
    ["/historical", { title: "Historical Analog", subtitle: `Compare current environmental conditions with historical climate patterns for ${locationName}.`, crumbs: ["Historical Analog"] }],
    ["/strategies", { title: "Crop Rotation Strategies", subtitle: "Compare example rotations and weight what matters most to you.", crumbs: ["Strategies"] }],
    ["/scenario", { title: "What If?", subtitle: "Explore how environmental changes could affect crop-rotation strategies.", crumbs: ["What If?"] }],
    ["/results", { title: "Comparison", subtitle: "Review the evidence, trade-offs and local-review needs.", crumbs: ["Results"] }],
    ["/crops", { title: "Crop Library", subtitle: "Crop traits and cited rule-table information used in comparisons.", crumbs: ["Crop Library"] }],
    ["/methodology", { title: "Methodology", subtitle: "How NASA observations, local information and ROTATE reasoning stay separate.", crumbs: ["Methodology"] }],
    ["/contact", { title: "Contact", subtitle: "Questions, feedback or collaboration ideas.", crumbs: ["Contact"] }],
  ];
  for (const [pattern, banner] of rules) {
    if (matchPath(pattern, pathname)) return banner;
  }
  return { title: "Not Found", subtitle: "We couldn't find that page.", crumbs: ["404"] };
}

export default function RootLayout() {
  const { pathname } = useLocation();
  const { selectedLocation } = useApp();

  useEffect(() => {
    if (!window.location.hash) window.scrollTo(0, 0);
  }, [pathname]);

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <Header />
      {pathname !== "/" && <PageBanner {...getBanner(pathname, selectedLocation.name)} />}
      <main className="flex-1">
        <Suspense fallback={<div className="mx-auto max-w-[1280px] px-6 py-16"><LoadingState label="Loading..." /></div>}>
          <Outlet />
        </Suspense>
      </main>
      <Footer flush={pathname === "/"} />
      <ScrollTopButton />
    </div>
  );
}
