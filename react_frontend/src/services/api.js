const API_BASE_URL = 'http://localhost:8000';

export async function fetchDashboardData() {
  const response = await fetch(`${API_BASE_URL}/`);
  return response.json();
}
