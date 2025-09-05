import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';

function backendDiscoveryPlugin() {
  const services = [
    'http://backend:59002',
    'http://backend-llm-cuda:59002',
    'http://backend-llm-amd:59002',
    'http://backend-llm-cpu:59002',
    'http://localhost:59002'
  ];

  let resolved = process.env.VITE_API_BASE;

  async function probe(url) {
    try {
      const res = await fetch(`${url}/`);
      return res.ok;
    } catch {
      return false;
    }
  }

  return {
    name: 'backend-discovery',
    async configureServer(server) {
      if (!resolved) {
        for (const url of services) {
          // eslint-disable-next-line no-await-in-loop
          if (await probe(url)) {
            resolved = url;
            break;
          }
        }
        if (!resolved) {
          resolved = 'http://localhost:59002';
        }
        process.env.VITE_API_BASE = resolved;
        console.log(`[backend] using ${resolved}`);
      }

      server.middlewares.use('/api-base', (_req, res) => {
        res.end(resolved);
      });
    }
  };
}

export default defineConfig({
        plugins: [
                sveltekit(),
                viteStaticCopy({
                        targets: [
                                {
                                        src: 'node_modules/@zaniar/effekseer-webgl-wasm/effekseer.wasm',
                                        dest: ''
                                }
                        ]
                }),
                backendDiscoveryPlugin()
        ],
        assetsInclude: ['**/*.efkefc']
});
