import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { createWave, listWaves } from "../api/waves";
import type { FocusType, Wave, WaveStatus } from "../types/domain";

const initialForm = {
  name: "",
  description: "",
  status: "active" as WaveStatus,
  focus_type: "mixed" as FocusType,
};

export function WavesPage() {
  const [waves, setWaves] = useState<Wave[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [formState, setFormState] = useState(initialForm);
  const activeCount = waves.filter((wave) => wave.status === "active").length;
  const pausedCount = waves.filter((wave) => wave.status === "paused").length;
  const archivedCount = waves.filter((wave) => wave.status === "archived").length;
  const totalRecords = waves.reduce((sum, wave) => sum + wave.record_count, 0);

  async function loadWaves() {
    setLoading(true);
    setLoadError(null);
    try {
      const data = await listWaves();
      setWaves(data);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : "Failed to load waves");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadWaves();
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setSubmitError(null);
    try {
      const trimmedName = formState.name.trim();
      const trimmedDescription = formState.description.trim();
      if (!trimmedName) {
        setSubmitError("Wave name is required.");
        return;
      }
      await createWave({
        ...formState,
        name: trimmedName,
        description: trimmedDescription,
      });
      setFormState(initialForm);
      await loadWaves();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to create wave");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="stack page-stack">
      <div className="hero-panel">
        <div className="hero-panel__content">
          <p className="eyebrow">Wave operations</p>
          <h2>Monitor signal pipelines without losing the thread.</h2>
          <p className="hero-copy">
            Stand up new waves, track their health, and jump straight into the
            workflows that need attention.
          </p>
        </div>
        <div className="stat-grid">
          <article className="stat-card">
            <span className="stat-card__label">Active waves</span>
            <strong className="stat-card__value">{activeCount}</strong>
            <span className="stat-card__hint">currently collecting or ready</span>
          </article>
          <article className="stat-card">
            <span className="stat-card__label">Paused waves</span>
            <strong className="stat-card__value">{pausedCount}</strong>
            <span className="stat-card__hint">held for review or maintenance</span>
          </article>
          <article className="stat-card">
            <span className="stat-card__label">Archived waves</span>
            <strong className="stat-card__value">{archivedCount}</strong>
            <span className="stat-card__hint">kept for history and audit</span>
          </article>
          <article className="stat-card">
            <span className="stat-card__label">Records tracked</span>
            <strong className="stat-card__value">{totalRecords}</strong>
            <span className="stat-card__hint">across every configured wave</span>
          </article>
        </div>
      </div>

      {loadError ? <p className="notice notice--error">{loadError}</p> : null}

      <div className="grid grid-2">
        <div className="panel">
          <div className="section-head">
            <div>
              <h2>Create Wave</h2>
              <p className="section-copy">
                Start a new monitoring lane with a clear focus and lifecycle
                state.
              </p>
            </div>
          </div>
          <form className="stack" onSubmit={onSubmit}>
            <label>
              Name
              <input
                required
                value={formState.name}
                onChange={(e) => setFormState({ ...formState, name: e.target.value })}
              />
            </label>
            <label>
              Description
              <textarea
                value={formState.description}
                onChange={(e) => setFormState({ ...formState, description: e.target.value })}
              />
            </label>
            <label>
              Status
              <select
                value={formState.status}
                onChange={(e) =>
                  setFormState({ ...formState, status: e.target.value as WaveStatus })
                }
              >
                <option value="active">active</option>
                <option value="paused">paused</option>
                <option value="archived">archived</option>
              </select>
            </label>
            <label>
              Focus Type
              <select
                value={formState.focus_type}
                onChange={(e) =>
                  setFormState({ ...formState, focus_type: e.target.value as FocusType })
                }
              >
                <option value="mixed">mixed</option>
                <option value="location">location</option>
                <option value="keyword">keyword</option>
                <option value="event">event</option>
              </select>
            </label>
            <button disabled={submitting} type="submit">
              {submitting ? "Creating..." : "Create Wave"}
            </button>
          </form>
          {submitError ? <p className="notice notice--error">{submitError}</p> : null}
        </div>

        <div className="panel">
          <div className="section-head">
            <div>
              <h2>Waves</h2>
              <p className="section-copy">
                Each wave groups connectors, records, discovery policy, and
                signal review in one place.
              </p>
            </div>
          </div>
          {loading ? <p>Loading waves...</p> : null}
          {!loading && waves.length === 0 ? (
            <div className="empty-state">
              <strong>No waves created yet.</strong>
              <p>
                Create your first wave to start collecting connectors, records,
                and alerts.
              </p>
            </div>
          ) : null}
          <ul className="stack">
            {waves.map((wave) => (
              <li key={wave.id} className="card">
                <div className="between">
                  <div>
                    <h3>{wave.name}</h3>
                    <p>{wave.description || "No description provided."}</p>
                  </div>
                  <span className={`status ${wave.status}`}>{wave.status}</span>
                </div>
                <p>
                  Focus: <strong>{wave.focus_type}</strong>
                </p>
                <p>
                  Connectors: {wave.connector_count} | Records: {wave.record_count}
                </p>
                <Link className="text-link" to={`/waves/${wave.id}`}>
                  Open Wave
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
