import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { viteStaticCopy } from 'vite-plugin-static-copy';

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
                })
        ],
        assetsInclude: ['**/*.efkefc']
});
