/**
 * StrategySchema v1 - minimal but comprehensive enough for wizard scaffolding.
 * Keep fields even if optional to match the planned API.
 */

export type UUID = string;

export type Tag = string;

export type IndicatorSource = 'price' | 'ohlcv' | 'indicator';
export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d';

export type IndicatorParam = {
  key: string;
  value: number | string | boolean;
};

export type IndicatorSpec = {
  id: string; // unique within strategy
  type: string; // e.g., 'sma', 'ema', 'rsi', 'macd'
  params?: IndicatorParam[];
  source?: {
    type: IndicatorSource;
    ref?: string; // when source=indicator, ref another indicator id
    field?: 'close' | 'open' | 'high' | 'low' | 'volume' | string;
  };
  timeframe?: Timeframe;
};

export type Operand =
  | { kind: 'const'; value: number | string | boolean }
  | { kind: 'indicator'; ref: string; field?: string }
  | { kind: 'price'; field: 'open' | 'high' | 'low' | 'close' | 'volume' }
  | { kind: 'expr'; expr: string };

export type Comparator = 'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'neq' | 'crosses_above' | 'crosses_below';

export type Condition = {
  left: Operand;
  op: Comparator;
  right: Operand;
};

export type BoolGroupOp = 'AND' | 'OR';

export type ConditionGroup = {
  op: BoolGroupOp;
  conditions: Condition[];
};

export type RuleSide = 'long' | 'short' | 'both';

export type EntryRules = {
  side: RuleSide;
  groups: ConditionGroup[]; // at least one
};

export type ExitRules = {
  side: RuleSide;
  groups: ConditionGroup[]; // can be empty to imply exits by stop/target only
};

export type SizingMode = 'fixed' | 'percent_of_equity' | 'volatility';

export type RiskControls = {
  maxPositions?: number;
  stopLossPct?: number; // 0-1
  takeProfitPct?: number; // 0-1
  trailingStopPct?: number; // 0-1
};

export type SizingConfig = {
  mode: SizingMode;
  params?: Record<string, number | string>;
  risk?: RiskControls;
};

export type AdvancedExpression = {
  id: string;
  expr: string;
};

export type StrategyBasics = {
  name: string;
  description?: string;
  tags?: Tag[];
};

export type StrategySchemaV1 = {
  version: '1';
  basics: StrategyBasics;
  indicators: IndicatorSpec[];
  entry: EntryRules;
  exit?: ExitRules;
  sizing: SizingConfig;
  advanced?: {
    expressions?: AdvancedExpression[];
  };
};

export type StrategyRecord = {
  id: UUID;
  status: 'draft' | 'published';
  created_at: string;
  updated_at: string;
  strategy: StrategySchemaV1;
};

export type StrategyStore = {
  strategies: StrategyRecord[];
};

/**
 * Minimal client-side validation helpers
 */
export function validateBasics(basics: StrategyBasics): string[] {
  const errs: string[] = [];
  if (!basics.name || !basics.name.trim()) errs.push('Name is required.');
  return errs;
}

export function validateIndicatorsUniqueIds(indicators: IndicatorSpec[]): string[] {
  const errs: string[] = [];
  const seen = new Set<string>();
  for (const ind of indicators) {
    const id = ind.id?.trim();
    if (!id) {
      errs.push('Indicator id is required.');
      continue;
    }
    if (seen.has(id)) errs.push(`Indicator id "${id}" is duplicated.`);
    seen.add(id);
  }
  return errs;
}

export function validateConditions(groups: ConditionGroup[] | undefined): string[] {
  const errs: string[] = [];
  if (!groups) return errs;
  groups.forEach((g, gi) => {
    if (!g.conditions || g.conditions.length === 0) {
      errs.push(`Group ${gi + 1} has no conditions.`);
      return;
    }
    g.conditions.forEach((c, ci) => {
      if (!c.left) errs.push(`Group ${gi + 1} condition ${ci + 1} missing left operand.`);
      if (!c.op) errs.push(`Group ${gi + 1} condition ${ci + 1} missing comparator.`);
      if (!c.right) errs.push(`Group ${gi + 1} condition ${ci + 1} missing right operand.`);
    });
  });
  return errs;
}

export function defaultStrategy(): StrategySchemaV1 {
  return {
    version: '1',
    basics: { name: '', description: '', tags: [] },
    indicators: [],
    entry: { side: 'both', groups: [{ op: 'AND', conditions: [] }] },
    exit: { side: 'both', groups: [] },
    sizing: { mode: 'fixed', params: { quantity: 1 }, risk: { maxPositions: 5 } },
    advanced: { expressions: [] },
  };
}