# Prof. Laio Oriel Seman
# DAS5102 - Fundamentos da Estrutura da Informação
# Code Visualizer

import ast
import inspect
import io
import keyword
import re

# ── Standard Library ─────────────────────────────────────────────
import sys
import time
import tokenize
from functools import wraps
from typing import Any, Dict, List, Tuple

import ipywidgets as widgets
import matplotlib.pyplot as plt

# ── Third-Party ──────────────────────────────────────────────────
import numpy as np
from adjustText import adjust_text
from IPython.display import Image, clear_output, display
from matplotlib import patches
from matplotlib import patheffects as pe
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.path import Path


class VizTheme:
    """Improved theme with cohesive, high-contrast, and modern tones"""
    colors = {
        # ── Syntax Highlighting ──────────────────────────
        'syntax_comment':    '#9AA0A6',  # Soft gray-blue
        'syntax_keyword':    '#D32F2F',  # Vivid red
        'syntax_function':   '#512DA8',  # Deep violet
        'syntax_string':     '#2E7D32',  # Dark green
        'syntax_number':     '#1976D2',  # Medium blue
        'syntax_builtin':    '#0288D1',  # Cyan-blue
        'syntax_class':      '#7B1FA2',  # Deep purple
        'syntax_operator':   '#C62828',  # Strong red
        'syntax_default':    '#212121',  # Nearly black

        # ── UI & Layout ─────────────────────────────────
        'current_line':            '#FFF59D',   # Soft yellow
        'current_line_indicator':  '#E53935',   # Red for current arrow
        'line_number_normal':      '#BDBDBD',   # Light gray
        'figure_background':       '#FAFAFA',   # Off-white

        # ── Headers & Progress ──────────────────────────
        'code_header_bg':    '#E3F2FD',  # Blue hint
        'memory_header_bg':  '#F3E5F5',  # Lavender hint
        'call_stack_text':   '#6A1B9A',  # Deep purple
        'call_stack_box':    '#F3E5F5',  # Light lavender
        'call_stack_arrow':  '#AB47BC',  # Purple
        'progress_bar':      '#43A047',  # Bright green
        'progress_bg':       '#E0E0E0',  # Light gray

        # ── Variables Box ───────────────────────────────
        'variables_bg':           '#E8F5E9',  # Very light green
        'variables_border':       '#388E3C',  # Green border
        'variables_title':        '#2E7D32',  # Dark green
        'variables_text_normal':  '#1B5E20',  # Very dark green
        'variables_text_changed': '#F57C00',  # Orange
        'variables_value':        '#43A047',  # Green value color

        # ── Object Box Colors ───────────────────────────
        'object_list_edge':   '#66BB6A',  # Soft green
        'object_list_face':   '#F1F8E9',  # Pale green
        'object_list_title':  '#2E7D32',  # Forest green

        'object_dict_edge':   '#FFA726',  # Orange
        'object_dict_face':   '#FFF3E0',  # Pale orange
        'object_dict_title':  '#EF6C00',  # Burnt orange

        'object_class_edge':  '#EC407A',  # Rose pink
        'object_class_face':  '#FCE4EC',  # Soft pink
        'object_class_title': '#AD1457',  # Deep rose

        'object_other_edge':  '#90A4AE',  # Blue-gray
        'object_other_face':  '#ECEFF1',  # Light blue-gray
        'object_other_title': '#455A64',  # Slate gray

        'object_ref_count':   '#616161',  # Neutral gray

        # ── Arrows / Connections ────────────────────────
        'connection_normal':   '#1E88E5',  # Blue
        'connection_changed':  '#FB8C00',  # Orange
        'connection_next':     '#F4511E',  # Deep orange
        'connection_prev':     '#EC407A',  # Pink
        'connection_left':     '#43A047',  # Bright green
        'connection_right':    '#2E7D32',  # Forest green
        'connection_parent':   '#FB8C00',  # Orange
        'connection_child':    '#EF6C00',  # Dark orange
        'connection_head':     '#8E24AA',  # Purple
        'connection_tail':     '#5E35B1',  # Deep purple
        'connection_fallback': '#546E7A',  # Gray-blue fallback

        # ── Connection Label Backgrounds ────────────────
        'label_bg_next':     '#FFEBEE',  # Soft red
        'label_bg_prev':     '#FCE4EC',  # Soft pink
        'label_bg_left':     '#E8F5E9',  # Soft green
        'label_bg_right':    '#E8F5E9',
        'label_bg_parent':   '#FFF3E0',  # Soft orange
        'label_bg_child':    '#FFF3E0',
        'label_bg_head':     '#F3E5F5',  # Lavender
        'label_bg_tail':     '#EDE7F6',  # Pale purple
        'label_bg_fallback': '#F5F5F5',  # Neutral light gray
        'label_bg_default':  '#FFFFFF',  # White

        # ── General / Extras ────────────────────────────
        'empty_state_text':  '#757575',  # Medium gray
        'bezier_arrow_bg':   '#FFFFFF',  # White background for bezier arrows
    }

    layouts = {
        'line_height': 0.025, 'box_padding': 0.15, 'var_line_spacing': 0.4,
        'obj_line_height': 0.28, 'progress_height': 0.02
    }

    fonts = {
        'code': 9, 'header': 14, 'var_label': 9,
        'object_label': 8, 'annotation': 7
    }

class CodeVisualizer:
    """
    CodeVisualizer is a Python class for visualizing the execution of code step-by-step, primarily intended for use in Jupyter notebooks or similar environments. It traces the execution of Python code, capturing the state of variables, objects, and the call stack at each step, and provides an interactive visualization of these states.
    Main Features:
    --------------
    - Traces Python code execution, capturing events such as line execution, function calls, and returns.
    - Records the state of local variables, objects, and the call stack at each step.
    - Detects and highlights changes in variables between steps.
    - Provides an interactive widget-based interface for navigating through execution steps, including controls for stepping, jumping to changes, and resetting.
    - Visualizes code, call stack, and memory (variables and objects) using matplotlib, with syntax highlighting and responsive layouts.
    - Handles complex data structures, including lists, dictionaries, and user-defined objects, with support for circular references.
    - Draws connections between variables and objects, and between objects via their attributes, with clear labeling and visual cues.
    Usage:
    ------
    1. Instantiate the CodeVisualizer.
    2. Use its `trace` method as a tracing function (e.g., with `sys.settrace`).
    3. After code execution, call the `show()` method to display the interactive visualization.
    Methods:
    --------
    - __init__(): Initializes the visualizer.
    - trace(frame, event, arg): Tracing function to capture execution steps.
    - show(): Displays the interactive visualization widget.
    - _render_step(step_idx): Renders a single execution step.
    - _calculate_layout(step): Determines the layout for visualization.
    - _create_grid(fig, layout_info): Sets up the matplotlib grid layout.
    - _draw_call_stack(ax, call_stack): Visualizes the call stack.
    - _draw_code(ax, step, step_idx): Visualizes the source code and highlights the current line.
    - _draw_memory(ax, state, changed_vars): Visualizes variables and objects in memory.
    - _draw_variables(...): Draws the variables section.
    - _draw_objects(...): Draws the objects section.
    - _draw_connections(...): Draws arrows between variables and objects.
    - _draw_object_connections(...): Draws arrows between objects via attributes.
    - _draw_single_connection(...): Draws a single curved arrow with label.
    - _capture_state(locals_dict): Captures the current state of variables and objects.
    - _detect_changes(current_locals): Detects which variables have changed.
    - _capture_args(frame): Captures function arguments.
    - _should_skip_frame(frame): Determines if a frame should be skipped from tracing.
    - _should_track_variable(name): Determines if a variable should be tracked.
    - _process_value(value, objects, processing): Processes a value for visualization.
    - _create_object_representation(value, objects, processing): Creates a representation for an object.
    - _extract_reference_id(attr_val): Extracts object reference ID from an attribute value.
    - _format_value(value): Formats a value for display.
    - _gather_all_references(variables, objects): Gathers all object references in the current frame.
    Dependencies:
    -------------
    - matplotlib
    - numpy
    - ipywidgets
    - inspect
    - tokenize
    - io
    - keyword
    Note:
    -----
    This class is designed for educational and debugging purposes, providing a visual and interactive way to understand Python code execution and memory state.
    """
    def __init__(self):
        self.steps, self.current_step, self.call_stack = [], 0, []
        self.root_filename = None
        self._cached_layout_info = None
        self._cached_fig = None
        self._cached_axes = None
        # Prepare label collector for adjustText
        self._text_labels = []

    def trace(self, frame, event, arg):
        """Enhanced tracing with better filtering and error handling"""
        if self.root_filename is None:
            self.root_filename = frame.f_code.co_filename

        if event not in ['line', 'call', 'return'] or self._should_skip_frame(frame):
            return self.trace

        try:
            lines, start = inspect.getsourcelines(frame.f_code)
            current_line = lines[frame.f_lineno - start].strip() if event == 'line' else ''
        except:
            return self.trace

        # Update call stack
        if event == 'call':
            self.call_stack.append({
                'func': frame.f_code.co_name, 'line': frame.f_lineno,
                'args': self._capture_args(frame)
            })
        elif event == 'return' and self.call_stack:
            self.call_stack.pop()

        # Skip empty/comment lines
        if event == 'line' and (not current_line or current_line.startswith('#')):
            return self.trace

        # Capture state + fingerprints
        state, fp_current = self._capture_state_from_stack(frame)

        # Detect mutated objects (container/content changed)
        mutated_objects = set()
        if self.steps:
            fp_prev = self.steps[-1].get('obj_fingerprints', {})
            # Compare only ids present in either step
            all_ids = set(fp_prev.keys()) | set(fp_current.keys())
            for oid in all_ids:
                if fp_prev.get(oid) != fp_current.get(oid):
                    mutated_objects.add(oid)

        # Detect variable changes (including “same ref, mutated object”)
        changed_vars = self._detect_changes(frame.f_locals, state, mutated_objects) if self.steps else []

        step_data = {
            'line_no': frame.f_lineno, 'current_line': current_line, 'source': lines,
            'start_line': start, 'vars': state,
            'func': frame.f_code.co_name, 'event': event, 'call_stack': list(self.call_stack),
            'changed_vars': changed_vars,
            'return_value': arg if event == 'return' else None,
            'timestamp': time.time(),
            'obj_fingerprints': fp_current,
            'mutated_objects': mutated_objects,
        }

        self.steps.append(step_data)
        return self.trace

    def _capture_state_from_stack(self, frame):
        """Capture variables/objects from frames in the root file, plus object fingerprints."""
        variables, objects = {}, {}
        fingerprints = {}
        seen_names = set()

        current = frame
        while current:
            if current.f_code.co_filename != self.root_filename:
                break

            for name, value in current.f_locals.items():
                if name in seen_names or not self._should_track_variable(name):
                    continue
                variables[name] = self._process_value(value, objects, processing=None, fp=fingerprints)
                seen_names.add(name)

            current = current.f_back

        return {'variables': variables, 'objects': objects}, fingerprints

    def _should_skip_frame(self, frame):
        """Check if frame should be skipped"""
        filename = frame.f_code.co_filename
        return 'site-packages' in filename or filename.startswith('<')
    
    def _capture_args(self, frame):
        """Capture function arguments"""
        code = frame.f_code
        return [(code.co_varnames[i], frame.f_locals[code.co_varnames[i]]) 
                for i in range(code.co_argcount) 
                if code.co_varnames[i] in frame.f_locals]
    
    def _detect_changes(self, current_locals, state, mutated_objects):
        """
        A variable is "changed" if:
        - its primitive value differs from previous step, OR
        - it’s a reference and the *pointed object mutated* this step.
        """
        if not self.steps:
            return []

        prev_vars = self.steps[-1]['vars']['variables']
        changed = []

        for name, value in current_locals.items():
            if not self._should_track_variable(name):
                continue

            cur_info = state['variables'].get(name)
            if cur_info is None:
                continue

            if cur_info['type'] == 'primitive':
                prev_val = prev_vars.get(name, {}).get('value', object())
                if prev_val != cur_info.get('value'):
                    changed.append(name)
            else:
                # Reference: mark changed if target object mutated
                target_id = cur_info.get('id')
                if target_id in mutated_objects:
                    changed.append(name)

        return changed

    
    def _capture_state(self, locals_dict):
        """Capture current variable and object state"""
        variables, objects = {}, {}
        for name, value in locals_dict.items():
            if self._should_track_variable(name):
                variables[name] = self._process_value(value, objects)
        return {'variables': variables, 'objects': objects}
    
    def _should_track_variable(self, name):
        """Determine if variable should be tracked"""
        return not name.startswith('_') and name not in ['inspect', 'sys']
    
    def _process_value(self, value, objects, processing=None, fp=None):
        """Process value and add/refresh objects in `objects` dict; track fingerprints in `fp`."""
        if processing is None:
            processing = set()

        # Primitives
        if value is None or isinstance(value, (int, float, str, bool)):
            return {'type': 'primitive', 'value': value}

        obj_id = id(value)
        # Compute/record fingerprint of this value (for containers/objects)
        if fp is not None:
            fp[obj_id] = self._make_fingerprint(value)

        # Already seen in this step?
        if obj_id in objects:
            # If our cached rep has a stale fingerprint, rebuild it
            cached_fp = objects[obj_id].get('_fp', None)
            current_fp = self._make_fingerprint(value)
            if cached_fp != current_fp:
                # Refresh representation in-place
                rep = self._create_object_representation(value, objects, processing)
                rep['_fp'] = current_fp
                objects[obj_id] = rep
            return {'type': 'ref', 'id': obj_id}

        # Circular reference protection
        if obj_id in processing:
            # Minimal shell to break the cycle; full rep will be built elsewhere
            objects[obj_id] = {'type': 'object', 'class': type(value).__name__, 'attrs': {}, '_fp': self._make_fingerprint(value)}
            return {'type': 'ref', 'id': obj_id}

        # New object: build representation
        processing.add(obj_id)
        try:
            rep = self._create_object_representation(value, objects, processing)
            rep['_fp'] = self._make_fingerprint(value)
            objects[obj_id] = rep
        finally:
            processing.discard(obj_id)

        return {'type': 'ref', 'id': obj_id}

    def _make_fingerprint(self, value):
        """
        Return a small, inexpensive fingerprint that changes when the container's
        shape or shallow content changes. Enough to detect appends/sets.
        """
        t = type(value)
        if t is list:
            # length + shallow type sketch of first/last few items
            n = len(value)
            head = tuple(type(x).__name__ for x in value[:3])
            tail = tuple(type(x).__name__ for x in value[-3:]) if n >= 3 else head
            return ('list', n, head, tail)
        if t is dict:
            n = len(value)
            # shallow key sketch (stable order via sorted repr of keys)
            try:
                keys_sample = tuple(sorted(map(lambda k: repr(k)[:16], list(value.keys())[:6])))
            except Exception:
                keys_sample = ('<keys>', n)
            return ('dict', n, keys_sample)
        if hasattr(value, '__dict__'):
            # number of public attrs + names sketch
            attrs = [a for a in value.__dict__.keys() if not a.startswith('_')]
            sample = tuple(sorted(attrs[:6]))
            return ('obj', type(value).__name__, len(attrs), sample)
        # primitives/others: identity is enough to ignore deep checks
        return ('prim', type(value).__name__)


    def _create_object_representation(self, value, objects, processing):
        """Create a lightweight but useful representation of an object."""
        # How many elements/fields to preview
        PREVIEW = 5

        if isinstance(value, list):
            return {
                'type': 'list', 'size': len(value),
                'items': [self._process_value(item, objects, processing) for item in value[:PREVIEW]]
            }
        if isinstance(value, dict):
            items = list(value.items())
            return {
                'type': 'dict', 'size': len(value),
                'items': {k: self._process_value(v, objects, processing) for k, v in items[:PREVIEW]}
            }

        # Generic Python object with attributes
        if hasattr(value, '__dict__'):
            attrs = {}
            count = 0
            for attr, attr_val in value.__dict__.items():
                if attr.startswith('_'):
                    continue
                attrs[attr] = self._process_value(attr_val, objects, processing)
                count += 1
                if count >= PREVIEW:
                    break
            return {'type': 'object', 'class': type(value).__name__, 'attrs': attrs}

        # Fallback
        return {'type': 'other', 'class': type(value).__name__}


    def show(self):
        if not self.steps:
            print("No execution steps captured!")
            return
        
        # Create controls
        slider = widgets.IntSlider(
            value=0, min=0, max=len(self.steps)-1, description='', readout=False,
            style={'handle_color': VizTheme.colors['progress_bar']}, layout=widgets.Layout(width='300px')
        )
        
        step_label = widgets.HTML(
            value=f"<b style='color: {VizTheme.colors['connection_normal']};'>Step 1 of {len(self.steps)}</b>",
            layout=widgets.Layout(margin='5px 0 0 10px')
        )
        
        # Navigation buttons
        btn_style = {'font_weight': 'bold'}
        buttons = {
            'prev': widgets.Button(description="← Prev", style=btn_style, layout=widgets.Layout(width='80px', height='35px')),
            'next': widgets.Button(description="Next →", style=btn_style, layout=widgets.Layout(width='80px', height='35px')),
            'change': widgets.Button(description="Next Change", style=btn_style, layout=widgets.Layout(width='100px', height='35px')),
            'call': widgets.Button(description="Next Call", style=btn_style, layout=widgets.Layout(width='90px', height='35px')),
            'reset': widgets.Button(description="⟲ Reset", style=btn_style, layout=widgets.Layout(width='80px', height='35px'))
        }
        
        output = widgets.Output()
        
        # Navigation functions
        def find_next_event(current_idx, condition):
            """Generic function to find next event matching condition"""
            for i in range(current_idx + 1, len(self.steps)):
                if condition(self.steps[i]):
                    return i
            return current_idx
        
        def update_display(step_idx=None):
            if step_idx is None:
                step_idx = slider.value
            
            with output:
                clear_output(wait=True)
                self._render_step(step_idx)
            
            step_label.value = f"<b style='color: {VizTheme.colors['connection_normal']};'>Step {step_idx + 1} of {len(self.steps)}</b>"
            buttons['prev'].disabled = (step_idx == 0)
            buttons['next'].disabled = (step_idx == len(self.steps) - 1)
        
        # Event handlers
        slider.observe(lambda change: update_display(change['new']), names='value')
        buttons['prev'].on_click(lambda b: setattr(slider, 'value', max(0, slider.value - 1)))
        buttons['next'].on_click(lambda b: setattr(slider, 'value', min(slider.max, slider.value + 1)))
        buttons['change'].on_click(lambda b: setattr(slider, 'value', 
            find_next_event(slider.value, lambda s: s['changed_vars'])))
        buttons['call'].on_click(lambda b: setattr(slider, 'value', 
            find_next_event(slider.value, lambda s: s['event'] == 'call')))
        buttons['reset'].on_click(lambda b: setattr(slider, 'value', 0))
        
        # Layout
        controls = widgets.VBox([
            widgets.HBox([buttons['prev'], buttons['next'], buttons['reset'], 
                         widgets.HTML("<div style='width: 20px;'></div>"), 
                         buttons['change'], buttons['call']]),
            widgets.HBox([slider, step_label])
        ], layout=widgets.Layout(margin='10px 0'))
        
        display(widgets.VBox([controls, output]))
        update_display(0)
        
    def _render_step(self, step_idx):
        """Enhanced rendering with better visual feedback"""
        step = self.steps[step_idx]
        layout_info = self._calculate_layout(step)

        fig = plt.figure(figsize=layout_info['fig_size'], 
                        facecolor=VizTheme.colors['figure_background'], dpi=150)
        axes = self._create_grid(fig, layout_info)

        # Add execution context info
        if step['event'] == 'call':
            context_info = f"→ Calling {step['func']}()"
        elif step['event'] == 'return':
            context_info = f"← Returning from {step['func']}()"
        else:
            context_info = f"Executing in {step['func']}()"
        
        fig.suptitle(context_info, fontsize=12, color=VizTheme.colors['call_stack_text'])

        # Draw components
        if axes['stack']:
            self._draw_call_stack(axes['stack'], step['call_stack'])
        self._draw_code(axes['code'], step, step_idx)
        self._draw_memory(axes['memory'], step['vars'], step['changed_vars'])

        fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)

        # Render to PNG buffer
        canvas = FigureCanvas(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)

        display(Image(data=buf.getvalue()))
        plt.close(fig)

    def _calculate_layout(self, step):
        """Calculate layout requirements"""
        num_objects = len(step['vars']['objects'])
        has_call_stack = bool(step['call_stack'])
        
        fig_width = 16 + min(6, num_objects * 0.8)
        fig_height = 10 + (2 if has_call_stack else 0) + min(4, num_objects * 0.3)
        
        return {
            'fig_size': (fig_width, fig_height),
            'has_call_stack': has_call_stack,
            'complex': has_call_stack and num_objects > 6
        }
    
    def _create_grid(self, fig, layout_info):
        """Create responsive grid layout"""
        if layout_info['complex']:
            gs = fig.add_gridspec(3, 2, height_ratios=[0.15, 1, 1.2], width_ratios=[1, 1.5])
            return {
                'stack': fig.add_subplot(gs[0, :]),
                'code': fig.add_subplot(gs[1, 0]),
                'memory': fig.add_subplot(gs[2, :])
            }
        elif layout_info['has_call_stack']:
            gs = fig.add_gridspec(2, 2, height_ratios=[0.12, 1], width_ratios=[1, 1.5])
            return {
                'stack': fig.add_subplot(gs[0, :]),
                'code': fig.add_subplot(gs[1, 0]),
                'memory': fig.add_subplot(gs[1, 1])
            }
        else:
            gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.5])
            return {'stack': None, 'code': fig.add_subplot(gs[0]), 'memory': fig.add_subplot(gs[1])}

    def _draw_call_stack(self, ax, call_stack):
        """Draw call stack - using theme colors"""
        ax.text(0.02, 0.7, "Call Stack:", fontweight='bold', fontsize=12, 
               transform=ax.transAxes, color=VizTheme.colors['call_stack_text'])
        
        stack = call_stack if call_stack else [{'func': 'main'}]
        x_pos = 0.15
        
        for i, call in enumerate(stack):
            ax.text(x_pos, 0.4, f"{call['func']}()", fontsize=10, transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=VizTheme.colors['call_stack_box'], alpha=0.8))
            
            if i < len(stack) - 1:
                ax.annotate('', xy=(x_pos + 0.12, 0.4), xytext=(x_pos + 0.08, 0.4),
                           arrowprops=dict(arrowstyle='->', color=VizTheme.colors['call_stack_arrow'], lw=2),
                           transform=ax.transAxes)
            x_pos += 0.15
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    def _draw_code(self, ax, step, step_idx):
        """Draw code section - using theme colors"""
        # Header
        header_text = f"Function: {step['func']}()"
        if step['event'] == 'return':
            header_text += f" → returns {step['return_value']}"
        elif step['changed_vars']:
            header_text += f" (modifying: {', '.join(step['changed_vars'])})"
        
        ax.text(0.5, 0.96, header_text, transform=ax.transAxes, 
               fontsize=13, fontweight='bold', ha='center', va='top',
               bbox=dict(boxstyle="round,pad=0.4", facecolor=VizTheme.colors['code_header_bg'], alpha=0.8))
        
        # Progress bar - using theme colors
        progress = (step_idx + 1) / len(self.steps)
        ax.add_patch(patches.Rectangle((0.05, 0.88), 0.9 * progress, 0.02, 
                    facecolor=VizTheme.colors['progress_bar'], alpha=0.8, transform=ax.transAxes))
        ax.add_patch(patches.Rectangle((0.05, 0.88), 0.9, 0.02, 
                    facecolor=VizTheme.colors['progress_bg'], alpha=0.5, transform=ax.transAxes))
        
        # Code lines
        self._draw_code_lines(ax, step)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    def _draw_code_lines(self, ax, step):
        """Draw code lines with context"""
        total_lines = len(step['source'])
        current_idx = step['line_no'] - step['start_line']
        
        # Calculate window
        max_lines = int(0.8 / 0.025)  # available_height / line_height
        
        if total_lines <= max_lines:
            start_show, end_show = 0, total_lines
        elif current_idx < total_lines * 0.2:
            start_show, end_show = 0, min(total_lines, max_lines)
        elif current_idx > total_lines * 0.8:
            context_size = min(max_lines, int(total_lines * 0.7))
            start_show, end_show = max(0, total_lines - context_size), total_lines
        else:
            context = min(max_lines // 2, total_lines // 3)
            start_show = max(0, current_idx - context)
            end_show = min(total_lines, start_show + max_lines)
        
        y_start = 0.82
        for i in range(start_show, end_show):
            line = step['source'][i].rstrip()
            line_no = step['start_line'] + i
            is_current = (line_no == step['line_no'])
            y = y_start - (i - start_show) * 0.025
            
            self._draw_code_line(ax, line, line_no, y, is_current, step)

    def _draw_code_line(self, ax, line, line_no, y, is_current, step):
        """Improved code line drawing - using theme colors"""
        
        # Current line highlighting
        if is_current:
            ax.add_patch(patches.Rectangle((0.02, y - 0.0125), 0.96, 0.025,
                facecolor=VizTheme.colors['current_line'], alpha=0.8, transform=ax.transAxes))
            ax.text(0.03, y, '▶', color=VizTheme.colors['current_line_indicator'], fontweight='bold', 
                fontsize=12, transform=ax.transAxes)
        
        # Line number
        line_color = VizTheme.colors['current_line_indicator'] if is_current else VizTheme.colors['line_number_normal']
        weight = 'bold' if is_current else 'normal'
        
        ax.text(0.08, y, f"{line_no:2d}", fontfamily='monospace', color=line_color, 
            fontweight=weight, fontsize=9, transform=ax.transAxes)
        
        # Code line with syntax highlighting (single text object - no overlapping!)
        display_line = line[:57] + "..." if len(line) > 60 else line
        
        if is_current:
            color = VizTheme.colors['current_line_indicator']
            weight = 'bold'
            style = 'normal'
        else:
            # Get syntax highlighting - handle both 2 and 3 return values
            result = self._get_syntax_highlighting(display_line)
            if isinstance(result, tuple) and len(result) == 3:
                color, weight, style = result
            elif isinstance(result, tuple) and len(result) == 2:
                color, weight = result
                # Determine style based on line content
                if (line.strip().startswith('#') or 
                    '"""' in line or "'''" in line):
                    style = 'italic'
                else:
                    style = 'normal'
            else:
                # Fallback
                color = VizTheme.colors['syntax_default']
                weight = 'normal'
                style = 'normal'
        
        # Draw the text with proper parameters
        ax.text(0.15, y, display_line, fontfamily='monospace', 
            color=color, fontweight=weight, fontstyle=style, 
            fontsize=9, transform=ax.transAxes)

    def _get_syntax_highlighting(self, line):
        """Clean syntax highlighting - using theme colors"""
        line_stripped = line.strip()
        
        # Comments
        if line_stripped.startswith('#'):
            return VizTheme.colors['syntax_comment'], 'normal'
        
        # Docstrings
        if ('"""' in line_stripped or "'''" in line_stripped):
            return VizTheme.colors['syntax_string'], 'normal'
        
        # Decorators
        if line_stripped.startswith('@'):
            return VizTheme.colors['syntax_function'], 'bold'
        
        # Class definitions
        if re.match(r'^\s*class\s+\w+', line_stripped):
            return VizTheme.colors['syntax_class'], 'bold'
        
        # Function definitions
        if re.match(r'^\s*(async\s+)?def\s+', line_stripped):
            return VizTheme.colors['syntax_function'], 'bold'
        
        # Import statements
        if re.match(r'^\s*(from\s+.+\s+)?import\s+', line_stripped):
            return VizTheme.colors['syntax_keyword'], 'bold'
        
        # Control flow keywords
        if re.search(r'\b(if|elif|else|for|while|try|except|return|yield)\b', line_stripped):
            return VizTheme.colors['syntax_keyword'], 'bold'
        
        # String literals
        if re.search(r'["\']', line_stripped):
            return VizTheme.colors['syntax_string'], 'normal'
        
        # Numbers
        if re.search(r'\b\d+\.?\d*\b', line_stripped):
            return VizTheme.colors['syntax_number'], 'normal'
        
        # Built-in functions (including Node)
        if re.search(r'\b(print|len|range|str|int|Node)\s*\(', line_stripped):
            return VizTheme.colors['syntax_builtin'], 'normal'
        
        # Function calls
        if re.search(r'\w+\s*\(', line_stripped):
            return VizTheme.colors['syntax_function'], 'normal'
        
        # Assignment operators
        if re.search(r'[\+\-\*\/]?=', line_stripped) and '==' not in line_stripped:
            return VizTheme.colors['syntax_operator'], 'normal'
        
        # Boolean/None
        if re.search(r'\b(True|False|None)\b', line_stripped):
            return VizTheme.colors['syntax_keyword'], 'bold'
        
        return VizTheme.colors['syntax_default'], 'normal'
    
    def _draw_memory(self, ax, state, changed_vars):
        """Draw memory state (variables and objects) with label adjustment support - using theme colors"""
        variables, objects = state['variables'], state['objects']
        all_refs = self._gather_all_references(variables, objects)

        header_text = "Memory State"
        if changed_vars:
            header_text += f" (★ {', '.join(changed_vars)} changed)"

        ax.text(0.5, 0.96, header_text, transform=ax.transAxes,
                fontsize=14, fontweight='bold', ha='center', va='top',
                bbox=dict(boxstyle="round,pad=0.4", facecolor=VizTheme.colors['memory_header_bg'], alpha=0.8))

        if not variables and not objects:
            ax.text(0.5, 0.5, "No variables or objects", ha='center', va='center',
                    fontsize=12, color=VizTheme.colors['empty_state_text'], transform=ax.transAxes)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return

        # Prepare canvas
        num_objects = len(objects)
        canvas_width = max(8, min(16, num_objects * 2.2))
        canvas_height = max(6, min(12, 4 + (num_objects // 4 + 1) * 2.8))

        ax.set_xlim(0, canvas_width)
        ax.set_ylim(0, canvas_height)

        # Draw variables and objects
        var_positions = self._draw_variables(ax, variables, changed_vars, canvas_width, canvas_height)
        obj_positions, attr_positions = self._draw_objects(
            ax, objects, 4 if variables else 0.5, canvas_width, canvas_height, all_refs
        )


        # Draw connections and collect label positions
        self._draw_connections(ax, variables, var_positions, objects, obj_positions, attr_positions, changed_vars)

        # Adjust labels to avoid overlaps (deferred)
        if self._text_labels:
            adjust_text(
                self._text_labels,
                autoalign='xy',
                only_move={'points': 'y', 'texts': 'xy'},
                force_points=0.3,
                force_text=0.1,
                expand_text=(1.1, 1.2),
                arrowprops=dict(arrowstyle='-', color='gray', lw=1, alpha=0.5)
            )

        ax.axis('off')

    def _draw_variables(self, ax, variables, changed_vars, canvas_width, canvas_height):
        """Draw variables section - using theme colors"""
        if not variables:
            return {}
        
        var_width = min(canvas_width * 0.25, 3.5)
        var_height = min(canvas_height * 0.6, 2 + len(variables) * 0.3)
        
        # Variables box
        ax.add_patch(patches.FancyBboxPatch(
            (0.5, canvas_height - var_height - 0.5), var_width, var_height,
            boxstyle="round,pad=0.15", facecolor=VizTheme.colors['variables_bg'], 
            edgecolor=VizTheme.colors['variables_border'], linewidth=2, alpha=0.9))
        
        ax.text(0.5 + var_width/2, canvas_height - 0.8, "Variables", 
               ha='center', fontweight='bold', fontsize=11, color=VizTheme.colors['variables_title'])
        
        var_positions = {}
        y_pos = canvas_height - 1.2
        line_spacing = min(0.4, var_height / (len(variables) + 1))
        
        for name, info in variables.items():
            is_changed = name in changed_vars
            type_label = "VAL" if info['type'] == 'primitive' else "REF"
            prefix = "★ " if is_changed else ""
            
            text_color = VizTheme.colors['variables_text_changed'] if is_changed else VizTheme.colors['variables_text_normal']
            
            ax.text(0.7, y_pos, f"{prefix}[{type_label}] {name}", 
                   fontweight='bold', fontsize=9, color=text_color)
            
            var_positions[name] = (0.5 + var_width, y_pos)
            
            if info['type'] == 'primitive':
                value_str = self._format_value(info['value'])
                value_color = VizTheme.colors['variables_text_changed'] if is_changed else VizTheme.colors['variables_value']
                ax.text(0.7, y_pos - 0.15, value_str, fontsize=8, 
                       color=value_color, style='italic')
            y_pos -= line_spacing
        
        return var_positions
    
    def _draw_objects(self, ax, objects, start_x, canvas_width, canvas_height, all_refs):
        """Draw object blocks and return their positions and anchor points for labels/arrows - using theme colors"""
        if not objects:
            return {}, {}

        positions, attr_positions = {}, {}
        n = len(objects)
        margin = 0.5
        available_w = canvas_width - start_x - margin

        # ─── Layout Strategy ──────────────────────────────────────────────
        def grid_parameters(n, available_w, max_w=2.5, pad=0.3):
            if available_w > 12: cols = 4
            elif available_w > 8: cols = 3
            else: cols = 2
            cols = min(cols, n)
            box_w = min(max_w, (available_w - (cols - 1) * pad) / cols)
            box_h = min(2.2, (canvas_height - 2) / ((n // cols) + 1))
            return cols, box_w, box_h, pad

        def object_colors(obj_type):
            """Get edge and face colors for object type from theme"""
            color_map = {
                'list': (VizTheme.colors['object_list_edge'], VizTheme.colors['object_list_face']),
                'dict': (VizTheme.colors['object_dict_edge'], VizTheme.colors['object_dict_face']),
                'object': (VizTheme.colors['object_class_edge'], VizTheme.colors['object_class_face']),
            }
            return color_map.get(obj_type, (VizTheme.colors['object_other_edge'], VizTheme.colors['object_other_face']))

        cols, box_w, box_h, pad = grid_parameters(n, available_w)

        for idx, (obj_id, obj) in enumerate(objects.items()):
            col, row = idx % cols, idx // cols
            x = start_x + col * (box_w + pad)
            y = canvas_height - 1.5 - row * (box_h + 0.4)

            if y - box_h < 0.2:
                break  # avoid drawing below canvas

            # ─── Draw object box ──────────────────────────────────────────
            edge_color, face_color = object_colors(obj.get('type', 'object'))
            ax.add_patch(patches.FancyBboxPatch(
                (x, y - box_h), box_w, box_h,
                boxstyle="round,pad=0.1",
                facecolor=face_color, edgecolor=edge_color,
                linewidth=2, alpha=0.95
            ))

            # ─── Title anchor: used for connections ───────────────────────
            title_anchor = (x + box_w / 2, y - 0.25)
            positions[obj_id] = title_anchor

            # ─── Reference count badge ────────────────────────────────────
            ref_count = sum(1 for ref in all_refs if ref == obj_id)
            if ref_count:
                ax.text(x + box_w - 0.1, y - 0.15, f"{ref_count} ref",
                        fontsize=7, ha="right", va="top", color=VizTheme.colors['object_ref_count'])

            # ─── Draw inner object content and capture attribute anchors ─
            anchors = self._draw_object_content(ax, obj, x, y, box_w, box_h)
            if anchors:
                attr_positions[obj_id] = anchors

        return positions, attr_positions

    def _draw_object_content(self, ax, obj, x, y, width, height):
        """Draw object content and return attribute positions with label-aligned arrow anchors - using theme colors"""
        type_colors = {
            'list': VizTheme.colors['object_list_title'], 
            'dict': VizTheme.colors['object_dict_title'], 
            'object': VizTheme.colors['object_class_title']
        }
        color = type_colors.get(obj['type'], VizTheme.colors['object_other_title'])
        title_size = max(9, min(12, width * 4))
        content_size = max(8, min(10, width * 3.5))
        attr_positions = {}

        def estimate_label_end(name, val_str, x_start):
            char_width = 0.008
            return x_start + char_width * (len(name) + len(val_str) + 2) + 0.03

        def draw_entry(label, val_str, y_pos, key):
            """Draw a single name:value pair and track position for connections."""
            label_x = x + 0.1
            value_x = label_x + 0.1 * (len(label) + 1)

            ax.text(label_x, y_pos, f"{label}:", fontsize=content_size, fontweight='bold')
            ax.text(value_x, y_pos, f"{val_str}", fontsize=content_size)

            attr_positions[key] = (estimate_label_end(label, val_str, label_x), y_pos)

        # Title
        title = obj.get('class') if obj['type'] == 'object' else f"{obj['type'].upper()}[{obj.get('size', '?')}]"
        ax.text(x + width / 2, y - 0.25, title,
                ha='center', fontweight='bold', color=color, fontsize=title_size)

        y_base = y - 0.5
        max_items = 10  # configurable if needed

        if obj['type'] == 'list':
            for i, item in enumerate(obj['items'][:max_items]):
                y_pos = y_base - i * 0.22
                name = f"[{i}]"
                val_str = self._format_value(item['value']) if item['type'] == 'primitive' else "→ obj"
                draw_entry(name, val_str, y_pos, str(i))

        elif obj['type'] == 'dict':
            for i, (key, val) in enumerate(list(obj['items'].items())[:max_items]):
                y_pos = y_base - i * 0.22
                name = str(key)[:8]
                val_str = self._format_value(val['value']) if val['type'] == 'primitive' else "→ obj"
                draw_entry(name, val_str, y_pos, str(key))

        elif obj['type'] == 'object':
            for i, (attr, val) in enumerate(list(obj['attrs'].items())[:max_items]):
                y_pos = y_base - i * 0.28
                name = str(attr)[:10]
                val_str = self._format_value(val['value']) if val['type'] == 'primitive' else "→ obj"
                draw_entry(name, val_str, y_pos, attr)

        return attr_positions

    def _draw_connections(self, ax, variables, var_pos, objects, obj_positions, attr_positions, changed_vars):
        """Draw connections between variables and objects - using theme colors"""
        # Variable to object connections
        for name, info in variables.items():
            if info['type'] == 'ref' and name in var_pos and info.get('id') in obj_positions:
                start = var_pos[name]
                end = obj_positions[info['id']]
                
                is_changed = name in changed_vars
                color = VizTheme.colors['connection_changed'] if is_changed else VizTheme.colors['connection_normal']
                lw = 4 if is_changed else 3
                
                ax.annotate('', xy=(end[0] - 1.2, end[1]), xytext=start,
                          arrowprops={'arrowstyle': '->', 'lw': lw, 'color': color, 'alpha': 0.9})
        
        # Object to object connections
        self._draw_object_connections(ax, objects, obj_positions, attr_positions)

    def draw_bezier_arrow(
        self,
        ax,
        start,
        end,
        label=None,
        arc=0.15,
        color='#2196F3',
        linewidth=3,
        label_bg='#FFFFFF',
        label_offset=0,
        zorder=2,
        fontsize=8,
        show_tail=True
    ):
        """Draw a curved Bezier arrow with normal-offset label and enhanced styling - using theme colors for background"""
        x0, y0 = start
        x1, y1 = end
        arc = np.clip(arc, -1.5, 1.5)

        dx, dy = x1 - x0, y1 - y0
        distance = np.hypot(dx, dy) + 1e-8
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        normal_x, normal_y = -dy / distance, dx / distance

        ctrl_x = mx + normal_x * arc
        ctrl_y = my + normal_y * arc

        path = Path(
            [start, (ctrl_x, ctrl_y), (ctrl_x, ctrl_y), end],
            [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        )

        arrow = mpatches.FancyArrowPatch(
            path=path,
            arrowstyle='-|>',
            color=color,
            lw=linewidth,
            alpha=0.9,
            zorder=zorder,
            mutation_scale=12
        )

        arrow.set_alpha(0.5)
        arrow.set_path_effects([
            pe.Stroke(linewidth=linewidth + 2, foreground=VizTheme.colors['bezier_arrow_bg']),
            pe.Normal()
        ])

        ax.add_patch(arrow)

        if show_tail:
            ax.plot(x0, y0, 'o', markersize=2.5, color=color, alpha=0.6, zorder=zorder - 1)

        # Optional: draw a circle around the arrow head (target object title)
        if label:
            # Draw an ellipse around the arrow target (typically object title)
            ell_w, ell_h = 0.8, 0.4  # width and height in data units — tune as needed
            ellipse = mpatches.Ellipse(
                (x1, y1), width=ell_w, height=ell_h,
                edgecolor=color,
                facecolor='none',
                linewidth=1.6,
                alpha=0.9,
                zorder=zorder + 1
            )
            ax.add_patch(ellipse)


        if label:
            label_x = mx + label_offset * 0.4 * normal_x
            label_y = my + label_offset * 0.4 * normal_y
            ax.text(
                label_x, label_y, label,
                fontsize=fontsize, ha='center', va='center',
                fontweight='bold', color=color,
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor=label_bg,
                    edgecolor=color,
                    linewidth=1.1,
                    alpha=0.97
                ),
                zorder=zorder + 3
            )

        show_tail = True
        if label and show_tail:
            underline_length = 0.4  # Tune based on font size and padding
            underline_y_offset = -0.05  # Slightly below the text

            ax.plot(
                [x0 - underline_length / 2, x0 + underline_length / 2],
                [y0 + underline_y_offset, y0 + underline_y_offset],
                color=color,
                linewidth=1.5,
                alpha=0.9,
                zorder=zorder + 1
            )

    def _draw_object_connections(self, ax, objects, obj_positions, attr_positions):
        """Draw curved arrows between object fields and target objects - using theme colors"""
        # Configuration for specific relationship types using theme colors
        style_by_attr = {
            'next':   {'color': VizTheme.colors['connection_next'], 'arc': 0.15,  'label_bg': VizTheme.colors['label_bg_next']},
            'prev':   {'color': VizTheme.colors['connection_prev'], 'arc': -0.15, 'label_bg': VizTheme.colors['label_bg_prev']},
            'left':   {'color': VizTheme.colors['connection_left'], 'arc': 0.25,  'label_bg': VizTheme.colors['label_bg_left']},
            'right':  {'color': VizTheme.colors['connection_right'], 'arc': -0.25, 'label_bg': VizTheme.colors['label_bg_right']},
            'parent': {'color': VizTheme.colors['connection_parent'], 'arc': 0.2,   'label_bg': VizTheme.colors['label_bg_parent']},
            'child':  {'color': VizTheme.colors['connection_child'], 'arc': -0.2,  'label_bg': VizTheme.colors['label_bg_child']},
            'head':   {'color': VizTheme.colors['connection_head'], 'arc': 0.3,   'label_bg': VizTheme.colors['label_bg_head']},
            'tail':   {'color': VizTheme.colors['connection_tail'], 'arc': -0.3,  'label_bg': VizTheme.colors['label_bg_tail']}
        }
        fallback_style = {'color': VizTheme.colors['connection_fallback'], 'arc': 0.1, 'label_bg': VizTheme.colors['label_bg_fallback']}

        # To avoid overlap when multiple arrows go between the same source-target
        jitter_tracker = {}
        label_offset_tracker = {}

        for obj_id, obj in objects.items():
            if obj.get('type') != 'object' or obj_id not in obj_positions:
                continue

            source_pos = obj_positions[obj_id]
            attr_anchors = attr_positions.get(obj_id, {})
            attrs = obj.get('attrs', {})

            # Prioritize known connection attributes like "next"
            for attr_name, attr_val in sorted(attrs.items(), key=lambda x: x[0] != 'next'):
                target_id = self._extract_reference_id(attr_val)
                if not target_id or target_id == obj_id or target_id not in obj_positions:
                    continue

                start_pos = attr_anchors.get(attr_name, source_pos)
                end_pos = obj_positions[target_id]

                # Apply jitter for visual separation
                jitter_key = (start_pos, end_pos)
                jitter = jitter_tracker.get(jitter_key, 0)
                jitter_tracker[jitter_key] = jitter + 0.05

                # Offset labels if stacked
                label_key = (start_pos, end_pos, attr_name)
                offset = label_offset_tracker.get(label_key, 0)
                label_offset_tracker[label_key] = offset + 1

                # Get style config
                style = style_by_attr.get(attr_name, fallback_style).copy()
                style['arc'] += jitter

                # Draw the connection
                self.draw_bezier_arrow(
                    ax, start_pos, end_pos,
                    label=attr_name,
                    arc=style.get('arc', 0.15),
                    color=style.get('color', VizTheme.colors['connection_normal']),
                    label_bg=style.get('label_bg', VizTheme.colors['label_bg_default']),
                    label_offset=offset
                )

    def _gather_all_references(self, variables, objects):
        """Return list of all object IDs referenced in current frame"""
        refs = []

        def extract_refs(val):
            if isinstance(val, dict):
                if val.get('type') == 'ref' and 'id' in val:
                    refs.append(val['id'])
                for v in val.values():
                    extract_refs(v)
            elif isinstance(val, list):
                for v in val:
                    extract_refs(v)

        for v in variables.values():
            extract_refs(v)
        for obj in objects.values():
            extract_refs(obj)

        return refs
        
    def _extract_reference_id(self, attr_val):
        """Extract reference ID from attribute value"""
        if isinstance(attr_val, dict) and attr_val.get('type') == 'ref':
            return attr_val.get('id')
        return None
    
    def _format_value(self, value):
        """Format value for display"""
        if isinstance(value, str):
            return f'"{value[:9]}..."' if len(value) > 12 else f'"{value}"'
        elif isinstance(value, float):
            return f"{value:.2f}"
        elif value is None:
            return 'None'
        return str(value)[:12]

def tracernaut(func):
    """
    Decorator that traces the execution of the decorated function using a CodeVisualizer.
    When applied, this decorator sets a trace function before calling the target function,
    capturing each execution step. If an exception occurs, it disables tracing, displays
    the captured steps (if any), and re-raises the exception. After execution, it prints
    the number of captured steps and displays them using the visualizer.
    Args:
        func (callable): The function to be decorated and traced.
    Returns:
        callable: The wrapped function with execution tracing enabled.
    Raises:
        Any exception raised by the decorated function is re-raised after tracing is stopped.
    Note:
        Requires a CodeVisualizer class with `trace`, `steps`, and `show()` methods.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        viz = CodeVisualizer()
        sys.settrace(viz.trace)
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            sys.settrace(None)
            print(f"Error during execution: {e}")
            if viz.steps:
                viz.show()
            raise
        finally:
            sys.settrace(None)
        
        print(f"✓ Captured {len(viz.steps)} execution steps for {func.__name__}()")
        if viz.steps:
            viz.show()
        else:
            print("  No steps captured - function may be too simple or fast")
        
        return result
    return wrapper
