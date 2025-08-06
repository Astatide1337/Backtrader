import React from 'react';
import Card, { CardContent, CardHeader } from 'components/ui/Card';
import Input from 'components/ui/Input';
import type { StrategySchemaV1 } from 'types/strategySchema';

type Props = {
  value: StrategySchemaV1['basics'];
  onChange: (v: StrategySchemaV1['basics']) => void;
  errors?: string[];
};

const StepBasics: React.FC<Props> = ({ value, onChange, errors }) => {
  const [tagsText, setTagsText] = React.useState((value.tags ?? []).join(', '));

  React.useEffect(() => {
    setTagsText((value.tags ?? []).join(', '));
  }, [value.tags]);

  const tagsFromText = (text: string) =>
    text
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean);

  return (
    <Card>
      <CardHeader>
        <h2 className="text-base font-semibold text-gray-900">Basics</h2>
        <p className="mt-1 text-sm text-gray-600">Name, description, and tags.</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <Input
            label="Name"
            name="name"
            value={value.name}
            onChange={(e) => onChange({ ...value, name: e.target.value })}
            placeholder="My Strategy"
            aria-required
            error={errors?.find((e) => e.toLowerCase().includes('name'))}
          />
          <Input
            label="Tags (comma-separated)"
            name="tags"
            value={tagsText}
            onChange={(e) => {
              setTagsText(e.target.value);
              onChange({ ...value, tags: tagsFromText(e.target.value) });
            }}
            placeholder="momentum, mean-reversion"
          />
          <div className="md:col-span-2">
            <label htmlFor="desc" className="mb-1 block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="desc"
              className="input min-h-[100px] w-full"
              value={value.description ?? ''}
              onChange={(e) => onChange({ ...value, description: e.target.value })}
              placeholder="Describe the strategy intent..."
            />
          </div>
        </div>
        {errors && errors.length > 0 && (
          <div role="alert" className="mt-3 rounded-md bg-red-50 p-2 text-sm text-red-700">
            {errors.map((e, i) => (
              <div key={i}>{e}</div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default React.memo(StepBasics);