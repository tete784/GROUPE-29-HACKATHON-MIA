const API_URL = 'http://localhost:3000/api/users';

export async function logout() {
  const token = localStorage.getItem('token');
  if (!token) return;

  await fetch(`${API_URL}/logout`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  localStorage.removeItem('token');
}