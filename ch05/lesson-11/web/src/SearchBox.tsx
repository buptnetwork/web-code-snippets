// #region all
interface SearchBoxProps {
  value: string;
  onValueChange: (value: string) => void;
}

export function SearchBox({ value, onValueChange }: SearchBoxProps) {
  return (
    <div className="search-bar">
      <label htmlFor="keyword">关键词</label>
      <input
        id="keyword"
        value={value}
        onChange={(event) => onValueChange(event.currentTarget.value)}
      />
    </div>
  );
}
// #endregion all
