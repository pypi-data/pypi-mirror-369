// types/rc-picker/index.d.ts
declare module 'rc-picker/lib/PickerPanel' {
  // 修正 defaultValue 类型，允许 null
  export interface BasePickerPanelProps<DateType> {
    defaultValue?: DateType | null;
  }
} 