// Prueba de carga de Frut Market con k6.
// Uso: k6 run -e BASE=https://frutmarket.pythonanywhere.com perf/k6_carga.js
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE = __ENV.BASE || 'https://frutmarket.pythonanywhere.com';

export const options = {
  // Sube a 10 usuarios simultáneos, se mantiene y baja (unos 50 segundos en total)
  stages: [
    { duration: '10s', target: 10 },
    { duration: '30s', target: 10 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],      // menos del 1% de errores
    http_req_duration: ['p(95)<1500'],   // el 95% responde en menos de 1.5 s
    // Umbrales por petición para ver el tiempo de cada una en el resumen
    'http_req_duration{nombre:pagina_principal}': ['p(95)<1500'],
    'http_req_duration{nombre:logo}': ['p(95)<1500'],
    'http_req_duration{nombre:login}': ['p(95)<1500'],
    'http_req_duration{nombre:api_inventario}': ['p(95)<1500'],
    'http_req_duration{nombre:api_resumen}': ['p(95)<1500'],
  },
  summaryTrendStats: ['avg', 'med', 'p(90)', 'p(95)', 'max'],
};

export function setup() {
  const r = http.post(`${BASE}/api/login`, JSON.stringify({ username: 'admin', password: 'admin123' }),
    { headers: { 'Content-Type': 'application/json' } });
  return { conSesion: r.status === 200 };
}

export default function (datos) {
  const pagina = http.get(`${BASE}/`, { tags: { nombre: 'pagina_principal' } });
  check(pagina, { 'página principal 200': (r) => r.status === 200 });

  const logo = http.get(`${BASE}/static/logo.jpeg`, { tags: { nombre: 'logo' } });
  check(logo, { 'logo 200': (r) => r.status === 200 });

  if (datos.conSesion) {
    http.post(`${BASE}/api/login`, JSON.stringify({ username: 'admin', password: 'admin123' }),
      { headers: { 'Content-Type': 'application/json' }, tags: { nombre: 'login' } });
    const inv = http.get(`${BASE}/api/inventario`, { tags: { nombre: 'api_inventario' } });
    check(inv, { 'inventario 200': (r) => r.status === 200 });
    const res = http.get(`${BASE}/api/resumen_general`, { tags: { nombre: 'api_resumen' } });
    check(res, { 'resumen 200': (r) => r.status === 200 });
  }
  sleep(1);
}
