import { Component, Input, Output, EventEmitter, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FieldDefinition } from '../../../core/models/objects.models';

@Component({
  selector: 'app-field-input',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './field-input.component.html',
})
export class FieldInputComponent {
  @Input({ required: true }) field!: FieldDefinition;
  @Input() value: unknown = null;
  @Input() error: string | null = null;
  @Output() valueChange = new EventEmitter<unknown>();

  readonly inputClass = `
    w-full px-3 py-2 rounded-lg text-sm
    bg-white dark:bg-slate-800
    border border-slate-200 dark:border-slate-700
    text-slate-900 dark:text-slate-100
    placeholder:text-slate-400 dark:placeholder:text-slate-500
    focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
    transition-colors
  `;

  inputType(): string {
    const map: Record<string, string> = {
      email: 'email',
      phone: 'tel',
      url: 'url',
    };
    return map[this.field.field_type] ?? 'text';
  }

  placeholder(): string {
    const map: Record<string, string> = {
      email: 'nombre@empresa.com',
      phone: '+57 300 000 0000',
      url: 'https://',
      relation: 'UUID del registro relacionado',
    };
    return map[this.field.field_type] ?? `Ingresa ${this.field.label.toLowerCase()}`;
  }

  onInput(event: Event): void {
    const val = (event.target as HTMLInputElement).value;
    this.onChange(val || null);
  }

  onSelectChange(event: Event): void {
    const val = (event.target as HTMLSelectElement).value;
    this.onChange(val || null);
  }

  onChange(val: unknown): void {
    this.valueChange.emit(val);
  }

  toggleMultiSelect(optValue: string): void {
    const current: string[] = Array.isArray(this.value) ? (this.value as string[]) : [];
    const next = current.includes(optValue)
      ? current.filter((v) => v !== optValue)
      : [...current, optValue];
    this.valueChange.emit(next.length ? next : null);
  }

  isSelected(optValue: string): boolean {
    return Array.isArray(this.value) && (this.value as string[]).includes(optValue);
  }
}
