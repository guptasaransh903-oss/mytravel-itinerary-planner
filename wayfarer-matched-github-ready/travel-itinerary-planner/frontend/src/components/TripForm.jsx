import { useState } from "react";

const TRAVEL_STYLES = [
  { value: "relaxed", label: "Relaxed" },
  { value: "balanced", label: "Balanced" },
  { value: "adventurous", label: "Adventurous" },
];

const INTEREST_OPTIONS = [
  { value: "food", label: "Food" },
  { value: "nature", label: "Nature" },
  { value: "culture", label: "Culture" },
  { value: "shopping", label: "Shopping" },
  { value: "history", label: "History" },
];

const INITIAL_FORM = {
  destination: "",
  start_date: "",
  end_date: "",
  budget_inr: "",
  travel_style: "balanced",
  interests: [],
};

function TripForm({ onSubmit, loading }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [errors, setErrors] = useState({});

  function updateField(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function toggleInterest(value) {
    setForm((prev) => {
      const exists = prev.interests.includes(value);
      return {
        ...prev,
        interests: exists
          ? prev.interests.filter((item) => item !== value)
          : [...prev.interests, value],
      };
    });
  }

  function validate() {
    const next = {};

    if (!form.destination.trim()) {
      next.destination = "Destination is required.";
    }

    if (!form.start_date) {
      next.start_date = "Start date is required.";
    }

    if (!form.end_date) {
      next.end_date = "End date is required.";
    }

    if (form.start_date && form.end_date && form.end_date < form.start_date) {
      next.end_date = "End date cannot be before the start date.";
    }

    const budget = Number(form.budget_inr);
    if (!form.budget_inr || Number.isNaN(budget) || budget <= 0) {
      next.budget_inr = "Enter a total budget greater than 0 (INR).";
    }

    if (!form.travel_style) {
      next.travel_style = "Choose a travel style.";
    }

    if (form.interests.length === 0) {
      next.interests = "Select at least one interest.";
    }

    setErrors(next);
    return Object.keys(next).length === 0;
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (!validate()) return;

    onSubmit({
      destination: form.destination.trim(),
      start_date: form.start_date,
      end_date: form.end_date,
      budget_inr: Number(form.budget_inr),
      travel_style: form.travel_style,
      interests: form.interests,
    });
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit} noValidate>
      <div className="field">
        <label htmlFor="destination">Destination</label>
        <input
          id="destination"
          name="destination"
          type="text"
          placeholder="e.g. Jaipur, India"
          value={form.destination}
          onChange={(e) => updateField("destination", e.target.value)}
          disabled={loading}
        />
        {errors.destination && <p className="field-error">{errors.destination}</p>}
      </div>

      <div className="field-row">
        <div className="field">
          <label htmlFor="start_date">Start date</label>
          <input
            id="start_date"
            name="start_date"
            type="date"
            value={form.start_date}
            onChange={(e) => updateField("start_date", e.target.value)}
            disabled={loading}
          />
          {errors.start_date && <p className="field-error">{errors.start_date}</p>}
        </div>

        <div className="field">
          <label htmlFor="end_date">End date</label>
          <input
            id="end_date"
            name="end_date"
            type="date"
            value={form.end_date}
            min={form.start_date || undefined}
            onChange={(e) => updateField("end_date", e.target.value)}
            disabled={loading}
          />
          {errors.end_date && <p className="field-error">{errors.end_date}</p>}
        </div>
      </div>

      <div className="field">
        <label htmlFor="budget_inr">Total budget (INR)</label>
        <input
          id="budget_inr"
          name="budget_inr"
          type="number"
          min="1"
          step="100"
          placeholder="e.g. 45000"
          value={form.budget_inr}
          onChange={(e) => updateField("budget_inr", e.target.value)}
          disabled={loading}
        />
        {errors.budget_inr && <p className="field-error">{errors.budget_inr}</p>}
      </div>

      <fieldset className="field" disabled={loading}>
        <legend>Travel style</legend>
        <div className="choice-row">
          {TRAVEL_STYLES.map((style) => (
            <label key={style.value} className="choice">
              <input
                type="radio"
                name="travel_style"
                value={style.value}
                checked={form.travel_style === style.value}
                onChange={(e) => updateField("travel_style", e.target.value)}
              />
              <span>{style.label}</span>
            </label>
          ))}
        </div>
        {errors.travel_style && (
          <p className="field-error">{errors.travel_style}</p>
        )}
      </fieldset>

      <fieldset className="field" disabled={loading}>
        <legend>Interests</legend>
        <div className="choice-row wrap">
          {INTEREST_OPTIONS.map((interest) => (
            <label key={interest.value} className="choice">
              <input
                type="checkbox"
                value={interest.value}
                checked={form.interests.includes(interest.value)}
                onChange={() => toggleInterest(interest.value)}
              />
              <span>{interest.label}</span>
            </label>
          ))}
        </div>
        {errors.interests && <p className="field-error">{errors.interests}</p>}
      </fieldset>

      <button className="btn primary" type="submit" disabled={loading}>
        {loading ? "Generating…" : "Generate Itinerary"}
      </button>
    </form>
  );
}

export default TripForm;
