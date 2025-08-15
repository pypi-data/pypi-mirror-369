<svelte:options accessors={true} />

<script lang="ts">
	// --- IMPORTS ---
	import { onMount } from "svelte";
	import type { Gradio } from "@gradio/utils";
	import TextBox from "./shared/Textbox.svelte";
	import { Block } from "@gradio/atoms";
	import { StatusTracker } from "@gradio/statustracker";
	import type { LoadingStatus } from "@gradio/statustracker";
	import { AutoTokenizer, env } from "@xenova/transformers";
	env.allowLocalModels = false;

	// --- GRADIO PROPS ---
	export let gradio: Gradio<{ change: never }>;
	export let value: {
		text: string;
		tokens: string[];
		token_ids: number[];
	} = { text: "", tokens: [], token_ids: [] };
	
	export let hide_input: boolean = false;
	export let model: string;
	export let display_mode: 'text' | 'token_ids' | 'hidden';
	export let model_max_length: number | undefined = undefined;
	export let preview_tokens: boolean = false

	// All other standard Textbox props
	export let label: string;
	export let info: string | undefined;
	export let elem_id: string;
	export let elem_classes: string[];
	export let visible: boolean;
	export let lines: number;
	export let placeholder: string;
	export let show_label: boolean;
	export let max_lines: number | undefined;
	export let type: "text" | "password" | "email";
	export let container: boolean;
	export let scale: number | null;
	export let min_width: number | undefined;
	export let submit_btn: string | boolean | null;
	export let stop_btn: string | boolean | null;
	export let show_copy_button: boolean;
	export let loading_status: LoadingStatus | undefined;
	export let rtl: boolean;
	export let text_align: "left" | "right" | undefined;
	export let autofocus: boolean;
	export let autoscroll: boolean;
	export let interactive: boolean;
	export let max_length: number | undefined;

	// --- INTERNAL STATE ---
	let tokenizer: any = null;
	let status: string = "Initializing...";	
	const colors = ["#d8b4fe", "#bbf7d0", "#fde047", "#fca5a5", "#93c5fd"];
	let currentModel: string = "";
	let lastTokenizedText: string | null = null; // Used to prevent infinite loops
	let detected_max_length: number | undefined = undefined;

	// --- CORE FUNCTIONS ---
	async function run_tokenization(text_to_process: string) {
		// Prevent re-tokenizing the same text, which breaks the reactive loop
		if (!tokenizer || text_to_process === lastTokenizedText) {
			return;
		}
		lastTokenizedText = text_to_process;

		try {
			const ids = tokenizer.encode(text_to_process);
			const tokens = ids.map((id: number) => tokenizer.decode([id]));
			
			// Update the single source of truth
			value = {
				text: text_to_process,
				tokens: tokens,
				token_ids: ids
			};
						
			// This updates the backend and populates the initial output.
			gradio.dispatch("change");

		} catch (e: any) {
			status = `Tokenization error: ${e.message}`;
		}
	}

	async function loadTokenizer(model_name: string) {
		if (currentModel === model_name && tokenizer) return;
		status = `Loading tokenizer: ${model_name}...`;
		currentModel = model_name;
		tokenizer = null;
		detected_max_length = undefined;

		try {
			tokenizer = await AutoTokenizer.from_pretrained(model_name);
			status = `Tokenizer "${model_name}" loaded.`;
			if (tokenizer.model_max_length) {
				detected_max_length = tokenizer.model_max_length;
			}
			// Reset the tracker and re-tokenize with the new model
			lastTokenizedText = null; 
			await run_tokenization(value.text); 
		} catch (e: any) {
			status = `Error loading model: ${e.message}`;
		}
	}

	// --- SVELTE LIFECYCLE AND REACTIVITY ---
	onMount(() => {
		loadTokenizer(model);
	});

	// This reactive statement watches the main 'value' prop.
	// When the backend pushes a new value, this will trigger re-tokenization.
	$: if (value && value.text !== undefined) {
		run_tokenization(value.text);
	}
	
	$: if (model && model !== currentModel) {
		loadTokenizer(model);
	}
	$: effective_max_length = detected_max_length !== undefined && detected_max_length != null ? detected_max_length : (model_max_length !== undefined && model_max_length != null ? model_max_length : null);
	$: token_count = value?.tokens?.length || 0;
	$: tokens_exceeded = effective_max_length ? token_count > effective_max_length : false;
</script>

<Block {visible} {elem_id} {elem_classes} {scale} {min_width} allow_overflow={false} padding={container}>
	{#if loading_status}
		<StatusTracker {...loading_status} on:clear_status={() => gradio.dispatch("clear_status", loading_status)} />
	{/if}

	<div class="component-header">
		{#if display_mode !== 'hidden'}
			<div class="visualization-toggle">
				<input type="checkbox" id="show-viz-{elem_id}" bind:checked={preview_tokens}>
				<label for="show-viz-{elem_id}">Preview tokens</label>
			</div>
			<div class="counters">
				<span class:exceeded={tokens_exceeded}>
					Tokens: {token_count}{#if effective_max_length}/{effective_max_length}{/if}
				</span>
				<span>Characters: {value?.text?.length || 0}</span>
			</div>
		{/if}
	</div>
	
	<!-- This now correctly uses the `hide_input` prop -->
	{#if !hide_input}
		<TextBox
			bind:value={value.text}
			{label}
			{info}
			{lines}
			{placeholder}
			{show_label}
			{max_lines}
			{type}
			{container}
			{submit_btn}
			{stop_btn}
			{show_copy_button}
			{rtl}
			{text_align}
			{autofocus}
			{autoscroll}
			{max_length}
			disabled={!interactive}
			on:change={() => gradio.dispatch("change")}
		/>
	{/if}
	
	<!-- The visualization panel -->
	{#if preview_tokens && display_mode !== 'hidden'}
		<div class="token-visualization-container">
			{#if display_mode === 'text'}
				<div class="token-display">
					{#if value?.tokens?.length > 0}
						{#each value.tokens as token, i}
							<span class="token" style="background-color: {colors[i % colors.length]};">
								{token.replace(/ /g, '\u00A0')}
							</span>
						{/each}
					{:else}
						<span class="status">{status}</span>
					{/if}
				</div>
			{:else if display_mode === 'token_ids'}
				<div class="token-display token-ids">
					{#if value?.token_ids?.length > 0}
						[{value.token_ids.join(", ")}]
					{:else}
						<span class="status">{status}</span>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</Block>

<style>	
	/* Styles for the header, counters, and toggle. */
	.component-header { 
		display: flex; 
		justify-content: space-between; 
		align-items: center; 
		margin-bottom: var(--spacing-sm); 
		min-height: 20px; 
	}
	.visualization-toggle { 
		display: flex; 
		align-items: center; 
		gap: 6px; 
		font-size: var(--text-sm); 
		color: var(--body-text-color); 
	}
	.visualization-toggle label { 
		cursor: pointer; 
		user-select: none; 
	}
		
	.visualization-toggle input[type="checkbox"] {
		/* Reset browser default styles */
		-webkit-appearance: none;
		-moz-appearance: none;
		appearance: none;

		/* Define our own box */
		width: 16px;
		height: 16px;
		border: 1px solid var(--body-text-color-subdued); /* A visible border in both themes */
		border-radius:  0; /*var(--radius-sm);*/
		background-color: var(--background-fill-primary);
		cursor: pointer;
		position: relative;
		display: inline-block;
		vertical-align: middle;
	}
	
	/* Style the checkmark itself using a pseudo-element */
	.visualization-toggle input[type="checkbox"]:checked::before {
		content: '✔'; /* You can also use an SVG here */
		position: absolute;
		font-size: 12px;
		font-weight: bold;
		top: 0px;
		left: 2px;
		/* Use a high-contrast color that works on both themes */
		color: var(--primary-500);
	}

	.visualization-toggle input[type="checkbox"]:focus {
		outline: 2px solid var(--primary-200); /* Add focus ring for accessibility */
	}

	.counters { 
		display: flex; 
		gap: var(--spacing-lg);
		font-size: var(--text-sm); 		
		/* Use a darker gray that is readable in light mode but still subdued */
		color: var(--neutral-500); 
		font-family: var(--font-mono); 
	}
	.counters span.exceeded {
		color: var(--color-red-500, #ef4444); 
		font-weight: var(--text-weight-bold);
	}
	/* Styles for the visualization panel */
	.token-visualization-container { 
		margin-top: var(--spacing-lg); 
	}
	.token-display { 
		color: #212529 !important; /* Force dark text on colored backgrounds */
		padding: var(--spacing-md); 
		border: 1px solid var(--border-color-primary); 
		background-color: var(--background-fill-secondary); 
		border-radius: var(--radius-lg); 
		min-height: 70px; 
		line-height: 1.8; 
		white-space: pre-wrap; 
		overflow-y: auto; 
		font-family: var(--font-mono); 
		font-size: var(--text-md); 
	}
	.token { 
		display: inline-block; 
		padding: var(--spacing-xs) var(--spacing-sm); 
		border-radius: var(--radius-lg); 
		margin: 2px; 
	}
	.token-ids { 
		word-break: break-all; 
	}
</style>