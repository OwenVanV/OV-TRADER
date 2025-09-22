import DashboardClient from "@/components/DashboardClient";
import { fetchDashboard } from "@/lib/api";

export default async function Page() {
  const data = await fetchDashboard();
  return <DashboardClient initialData={data} />;
}
