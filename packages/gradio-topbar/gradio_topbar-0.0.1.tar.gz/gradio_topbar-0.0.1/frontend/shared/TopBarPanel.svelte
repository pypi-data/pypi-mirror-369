<!-- frontend/shared/TopBarPanel.svelte -->

<script lang="ts">
	import { createEventDispatcher, onMount } from "svelte";
	const dispatch = createEventDispatcher<{
		expand: void;
		collapse: void;
	}>();

	export let open = true;
	export let height: number | string;
	export let width: number | string;
	export let bring_to_front = false;

	let mounted = false;
	let _open = false;

	let width_css = typeof width === "number" ? `${width}px` : width;
	let height_css = typeof height === "number" ? `${height}px` : height;
	let prefersReducedMotion: boolean;

	onMount(() => {
		mounted = true;
		const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
		prefersReducedMotion = mediaQuery.matches;

		const updateMotionPreference = (e: MediaQueryListEvent): void => {
			prefersReducedMotion = e.matches;
		};
		mediaQuery.addEventListener("change", updateMotionPreference);
		return () => {
			mediaQuery.removeEventListener("change", updateMotionPreference);
		};
	});

	$: if (mounted) _open = open;
</script>

<div
	class="top-bar"
	class:open={_open}
	class:reduce-motion={prefersReducedMotion}
	class:on-top={bring_to_front}
	style="height: {height_css}; width: {width_css};"
>
	<button
		on:click={() => {
			_open = !_open;
			open = _open;
			if (_open) {
				dispatch("expand");
			} else {
				dispatch("collapse");
			}
		}}
		class="toggle-top-button"
		aria-label="Toggle Top Bar"
	>
		<div class="chevron">
			<span class="chevron-arrow"></span>
		</div>
	</button>
	<div class="bar-content">
		<slot />
	</div>
</div>

<style>
	.top-bar {
		display: flex;
		flex-direction: column;
		position: fixed;
		top: 0;
		left: 50%;
		background-color: var(--background-fill-secondary);
		transform: translateX(-50%) translateY(-100%);
		z-index: 1000;
		border-bottom: 1px solid var(--border-color-primary);
		box-shadow: 0 2px 5px rgba(0,0,0,0.05);
	}

	.top-bar.on-top {
		z-index: 2000;
	}

	.top-bar:not(.reduce-motion) {
		transition: transform 0.3s ease-in-out;
	}

	.top-bar.open {
		transform: translateX(-50%) translateY(0);
	}

	.toggle-top-button {
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translate(-50%, 100%);
		background: var(--background-fill-secondary);
		border: 1px solid var(--border-color-primary);
		border-top: none;
		cursor: pointer;
		padding: var(--size-2);
		display: flex;
		align-items: center;
		justify-content: center;
		width: var(--size-10);
		height: var(--size-6);
		z-index: inherit;
		border-radius: 0 0 var(--radius-lg) var(--radius-lg);
	}

	.toggle-top-button:not(.reduce-motion) {
		transition: all 0.3s ease-in-out;
	}

	.chevron {
		position: relative;
		display: block;
		width: var(--size-3);
		height: var(--size-3);
	}

	.chevron-arrow {
		position: absolute;
		box-sizing: border-box;
		top: 10%;
		left: 18%;
		width: 80%;
		height: 80%;
		border-bottom: var(--size-0-5) solid var(--body-text-color);
		border-right: var(--size-0-5) solid var(--body-text-color);
		transform: rotate(45deg);
	}

	.top-bar:not(.reduce-motion) .chevron-arrow {
		transition: transform 0.3s ease-in-out;
	}

	.top-bar.open .chevron-arrow {
		transform: rotate(-135deg);
	}

	.bar-content {
		padding: var(--size-4);
		overflow-y: auto;
		flex-grow: 1;
	}
</style>