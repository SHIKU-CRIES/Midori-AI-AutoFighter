<script>
	import favicon from '$lib/assets/favicon.svg';
	import PingIndicator from '$lib/PingIndicator.svelte';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<!-- Add the persistent ping indicator to all pages -->
<PingIndicator />

{@render children?.()}
