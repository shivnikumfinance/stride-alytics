import { Card, Input, Select, Button } from "../ui";
import { useScreenerStore } from "../../store";

export function FilterPanel() {
  const filters = useScreenerStore((s) => s.filters);
  const setFilters = useScreenerStore((s) => s.setFilters);
  const resetFilters = useScreenerStore((s) => s.resetFilters);

  return (
    <Card title="Filters" subtitle="Narrow the options chain" bodyClassName="space-y-4">
      <Input
        label="Symbol"
        name="symbol"
        value={filters.symbol}
        onChange={(e) => setFilters({ symbol: e.target.value.toUpperCase() })}
        placeholder="AAPL"
      />
      <div className="grid grid-cols-2 gap-3">
        <Input
          label="Min strike"
          name="min_strike"
          type="number"
          value={filters.min_strike ?? ""}
          onChange={(e) => setFilters({ min_strike: e.target.value === "" ? null : Number(e.target.value) })}
        />
        <Input
          label="Max strike"
          name="max_strike"
          type="number"
          value={filters.max_strike ?? ""}
          onChange={(e) => setFilters({ max_strike: e.target.value === "" ? null : Number(e.target.value) })}
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Input
          label="Expiry min (days)"
          name="expiry_days_min"
          type="number"
          value={filters.expiry_days_min}
          onChange={(e) => setFilters({ expiry_days_min: Number(e.target.value) })}
        />
        <Input
          label="Expiry max (days)"
          name="expiry_days_max"
          type="number"
          value={filters.expiry_days_max}
          onChange={(e) => setFilters({ expiry_days_max: Number(e.target.value) })}
        />
      </div>
      <Select
        label="Option type"
        name="option_type"
        value={filters.option_type ?? ""}
        onChange={(e) => setFilters({ option_type: (e.target.value || null) as any })}
      >
        <option value="">Both</option>
        <option value="call">Calls</option>
        <option value="put">Puts</option>
      </Select>
      <div className="grid grid-cols-2 gap-3">
        <Input
          label="Min volume"
          name="min_volume"
          type="number"
          value={filters.min_volume}
          onChange={(e) => setFilters({ min_volume: Number(e.target.value) })}
        />
        <Input
          label="Min OI"
          name="min_open_interest"
          type="number"
          value={filters.min_open_interest}
          onChange={(e) => setFilters({ min_open_interest: Number(e.target.value) })}
        />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Input
          label="Min IV"
          name="min_iv"
          type="number"
          step="0.01"
          value={filters.min_iv ?? ""}
          onChange={(e) => setFilters({ min_iv: e.target.value === "" ? null : Number(e.target.value) })}
          hint="0.30 = 30%"
        />
        <Input
          label="Max IV"
          name="max_iv"
          type="number"
          step="0.01"
          value={filters.max_iv ?? ""}
          onChange={(e) => setFilters({ max_iv: e.target.value === "" ? null : Number(e.target.value) })}
        />
      </div>
      <Input
        label="Limit"
        name="limit"
        type="number"
        value={filters.limit}
        onChange={(e) => setFilters({ limit: Number(e.target.value) })}
        hint="Free: 50 max · Pro: 10,000 max"
      />
      <div className="flex gap-2">
        <Button type="button" variant="secondary" onClick={resetFilters} className="flex-1">
          Reset
        </Button>
      </div>
    </Card>
  );
}
