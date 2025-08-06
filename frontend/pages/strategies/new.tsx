import React from 'react';
import { useRouter } from 'next/router';
import WizardLayout from 'components/strategies/WizardLayout';
import StepBasics from 'components/strategies/StepBasics';
import StepIndicators from 'components/strategies/StepIndicators';
import StepEntryRules from 'components/strategies/StepEntryRules';
import StepExitRules from 'components/strategies/StepExitRules';
import StepSizingRisk from 'components/strategies/StepSizingRisk';
import StepAdvanced from 'components/strategies/StepAdvanced';
import StepReview from 'components/strategies/StepReview';
import Button from 'components/ui/Button';
import Card, { CardContent } from 'components/ui/Card';
import {
  defaultStrategy,
  validateBasics,
  validateIndicatorsUniqueIds,
  validateConditions,
  type StrategySchemaV1,
} from 'types/strategySchema';
import { createOrUpdateCustomStrategy } from 'lib/customStrategies';

const steps = [
  { key: 'basics', title: 'Basics', description: 'Name, description, tags' },
  { key: 'indicators', title: 'Indicators', description: 'Define indicators' },
  { key: 'entry', title: 'Entry Rules', description: 'Side and logic' },
  { key: 'exit', title: 'Exit Rules', description: 'Optional exit logic' },
  { key: 'sizing', title: 'Sizing & Risk', description: 'Position sizing and controls' },
  { key: 'advanced', title: 'Advanced', description: 'Optional expressions' },
  { key: 'review', title: 'Review & Validate', description: 'Preview, simulate, save' },
] as const;

const NewCustomStrategyPage: React.FC = () => {
  const router = useRouter();
  const [active, setActive] = React.useState(0);
  const [schema, setSchema] = React.useState<StrategySchemaV1>(() => defaultStrategy());
  const [busy, setBusy] = React.useState(false);

  function next() {
    setActive((i) => Math.min(i + 1, steps.length - 1));
  }
  function back() {
    setActive((i) => Math.max(i - 1, 0));
  }

  // Aggregate minimal validations per step
  const basicsErrors = validateBasics(schema.basics);
  const indicatorErrors = validateIndicatorsUniqueIds(schema.indicators);
  const entryErrors = validateConditions(schema.entry.groups);
  const exitErrors = (schema.exit?.groups?.length ?? 0) > 0 ? validateConditions(schema.exit?.groups) : [];
  const localErrors = [...basicsErrors, ...indicatorErrors, ...entryErrors, ...exitErrors];

  const canNextByStep = (idx: number) => {
    if (idx === 0) return basicsErrors.length === 0;
    if (idx === 1) return indicatorErrors.length === 0;
    if (idx === 2) return entryErrors.length === 0;
    return true;
  };

  async function onSaved(rec: { id: string }) {
    router.push(`/strategies/custom/${encodeURIComponent(rec.id)}`);
  }

  function renderStep() {
    switch (steps[active].key) {
      case 'basics':
        return (
          <StepBasics
            value={schema.basics}
            onChange={(v) => setSchema((s) => ({ ...s, basics: v }))}
            errors={basicsErrors}
          />
        );
      case 'indicators':
        return (
          <StepIndicators
            value={schema.indicators}
            onChange={(v) => setSchema((s) => ({ ...s, indicators: v }))}
          />
        );
      case 'entry':
        return (
          <StepEntryRules
            value={schema.entry}
            onChange={(v) => setSchema((s) => ({ ...s, entry: v }))}
          />
        );
      case 'exit':
        return (
          <StepExitRules
            value={schema.exit}
            onChange={(v) => setSchema((s) => ({ ...s, exit: v }))}
          />
        );
      case 'sizing':
        return (
          <StepSizingRisk
            value={schema.sizing}
            onChange={(v) => setSchema((s) => ({ ...s, sizing: v }))}
          />
        );
      case 'advanced':
        return (
          <StepAdvanced
            value={schema.advanced}
            onChange={(v) => setSchema((s) => ({ ...s, advanced: v }))}
          />
        );
      case 'review':
        return <StepReview schema={schema} setBusy={setBusy} onSaved={onSaved as any} localErrors={localErrors} />;
      default:
        return null;
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-semibold text-gray-900">New Custom Strategy</h1>
              <p className="text-sm text-gray-600">Build a strategy with schema-driven wizard.</p>
            </div>
            <div className="hidden gap-2 md:flex">
              <Button variant="secondary" size="sm" onClick={back} disabled={active === 0 || busy}>
                Back
              </Button>
              {active < steps.length - 1 ? (
                <Button size="sm" onClick={next} disabled={!canNextByStep(active) || busy}>
                  Next
                </Button>
              ) : (
                <Button
                  size="sm"
                  onClick={async () => {
                    // quick draft save to navigate to detail
                    const rec = await createOrUpdateCustomStrategy(schema, 'draft');
                    router.push(`/strategies/custom/${encodeURIComponent(rec.id)}`);
                  }}
                  disabled={busy}
                >
                  Save Draft
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <WizardLayout
        steps={steps as any}
        activeIndex={active}
        onSelectStep={(i) => setActive(i)}
      >
        <div className="space-y-4">
          {renderStep()}
          {/* Mobile nav */}
          <div className="flex items-center justify-between md:hidden">
            <Button variant="secondary" size="sm" onClick={back} disabled={active === 0 || busy}>
              Back
            </Button>
            {active < steps.length - 1 ? (
              <Button size="sm" onClick={next} disabled={!canNextByStep(active) || busy}>
                Next
              </Button>
            ) : (
              <Button
                size="sm"
                onClick={async () => {
                  const rec = await createOrUpdateCustomStrategy(schema, 'draft');
                  router.push(`/strategies/custom/${encodeURIComponent(rec.id)}`);
                }}
                disabled={busy}
              >
                Save Draft
              </Button>
            )}
          </div>
        </div>
      </WizardLayout>
    </div>
  );
};

export default NewCustomStrategyPage;