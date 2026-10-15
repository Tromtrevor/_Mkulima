import { useState } from "react";
import {
  Sprout,
  MapPinned,
  CloudRain,
  TrendingUp,
  RefreshCw,
  MapPin,
  CalendarDays,
  CheckCircle2,
  AlertCircle,
  LoaderCircle,
  ArrowUpRight,
  Database,
} from "lucide-react";

import StatCard from "../components/StatCard";
import {
  getFarm,
  getFarmLocation,
  collectFarmFeatures,
  createPrediction,
  getFarmPredictions,
} from "../services/api";

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }

  return error?.message || "Something went wrong. Please try again.";
}

function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined || value === "") return "—";

  const number = Number(value);
  return Number.isFinite(number)
    ? number.toLocaleString(undefined, { maximumFractionDigits: decimals })
    : String(value);
}

function DataRow({ label, value }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-stone-100 py-3 last:border-0">
      <span className="text-sm text-stone-500">{label}</span>
      <span className="max-w-[60%] break-words text-right text-sm font-medium text-stone-800">
        {value ?? "—"}
      </span>
    </div>
  );
}

export default function Dashboard() {
  const [farmId, setFarmId] = useState("1");
  const [cycleId, setCycleId] = useState("1");
  const [observationDate, setObservationDate] = useState(
    new Date().toISOString().slice(0, 10)
  );

  const [farm, setFarm] = useState(null);
  const [location, setLocation] = useState(null);
  const [features, setFeatures] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const validIds = () =>
    Number(farmId) > 0 &&
    Number.isInteger(Number(farmId)) &&
    Number(cycleId) > 0 &&
    Number.isInteger(Number(cycleId));

  function resetMessages() {
    setError("");
    setNotice("");
  }

  async function loadFarm() {
    resetMessages();

    if (!validIds()) {
      setError("Enter valid positive integer farm and crop cycle IDs.");
      return;
    }

    setLoading("farm");

    try {
      const [farmResponse, locationResponse, historyResponse] =
        await Promise.allSettled([
          getFarm(farmId),
          getFarmLocation(farmId),
          getFarmPredictions(farmId),
        ]);

      if (farmResponse.status === "rejected") {
        throw farmResponse.reason;
      }

      setFarm(farmResponse.value.data);

      setLocation(
        locationResponse.status === "fulfilled"
          ? locationResponse.value.data
          : null
      );

      setHistory(
        historyResponse.status === "fulfilled"
          ? Array.isArray(historyResponse.value.data)
            ? historyResponse.value.data
            : historyResponse.value.data?.predictions || []
          : []
      );

      if (
        locationResponse.status === "rejected" ||
        historyResponse.status === "rejected"
      ) {
        setNotice(
          "Farm loaded. Location or prediction history could not be retrieved."
        );
      } else {
        setNotice("Farm details loaded successfully.");
      }

      setFeatures(null);
      setPrediction(null);
    } catch (err) {
      setFarm(null);
      setLocation(null);
      setFeatures(null);
      setPrediction(null);
      setError(getErrorMessage(err));
    } finally {
      setLoading("");
    }
  }

  async function loadFeatures() {
    resetMessages();

    if (!validIds()) {
      setError("Enter valid farm and crop cycle IDs.");
      return;
    }

    if (!observationDate) {
      setError("Choose an observation date.");
      return;
    }

    setLoading("features");

    try {
      const response = await collectFarmFeatures(
        farmId,
        cycleId,
        observationDate
      );

      setFeatures(response.data);
      setNotice("Farm features collected and saved successfully.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading("");
    }
  }

  async function runPrediction() {
    resetMessages();

    if (!validIds()) {
      setError("Enter valid farm and crop cycle IDs.");
      return;
    }

    setLoading("prediction");

    try {
      const response = await createPrediction(farmId, cycleId);
      setPrediction(response.data);

      try {
        const historyResponse = await getFarmPredictions(farmId);
        setHistory(
          Array.isArray(historyResponse.data)
            ? historyResponse.data
            : historyResponse.data?.predictions || []
        );
      } catch {
        // The prediction itself succeeded; history can be refreshed later.
      }

      setNotice("Yield prediction generated and saved successfully.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading("");
    }
  }

  const weather = features?.weather || {};
  const ndvi = features?.ndvi || {};
  const soil = features?.soil || {};
  const elevation = features?.elevation || {};

  const predictedYield =
    prediction?.predicted_yield ??
    prediction?.yield_kg_ha ??
    null;

  const farmName =
    farm?.name ||
    farm?.farm_name ||
    `Farm ${farmId || "—"}`;

  return (
    <div className="space-y-7">
      <section className="relative overflow-hidden rounded-3xl bg-[#10251d] p-6 text-white md:p-8">
        <div className="pointer-events-none absolute -right-10 -top-20 h-64 w-64 rounded-full border-[40px] border-white/5" />
        <div className="pointer-events-none absolute -bottom-28 right-36 h-56 w-56 rounded-full bg-lime-400/10 blur-2xl" />

        <div className="relative grid gap-8 lg:grid-cols-[1.3fr_0.7fr] lg:items-center">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-lime-300/20 bg-lime-300/10 px-3 py-1.5 text-xs font-medium text-lime-200">
              <Sprout size={14} />
              Precision agriculture
            </span>

            <h1 className="mt-5 max-w-xl text-3xl font-semibold leading-tight tracking-tight md:text-4xl">
              Better farm data.
              <span className="block text-lime-300">
                Smarter decisions.
              </span>
            </h1>

            <p className="mt-4 max-w-xl text-sm leading-6 text-emerald-50/65">
              Collect environmental and soil features, analyze farm
              conditions, and generate maize yield estimates from your
              geospatial data pipeline.
            </p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
            <div className="mb-4 flex items-center gap-2">
              <MapPinned className="text-lime-300" size={19} />
              <h2 className="font-semibold">Select a farm</h2>
            </div>

            <form
              className="space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                loadFarm();
              }}
            >
              <div className="grid grid-cols-2 gap-3">
                <label className="block text-xs text-emerald-50/70">
                  Farm ID
                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={farmId}
                    onChange={(event) => setFarmId(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-white/10 bg-[#19382b] px-3 py-3 text-sm text-white outline-none focus:border-lime-300"
                    required
                  />
                </label>

                <label className="block text-xs text-emerald-50/70">
                  Crop cycle ID
                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={cycleId}
                    onChange={(event) => setCycleId(event.target.value)}
                    className="mt-2 w-full rounded-xl border border-white/10 bg-[#19382b] px-3 py-3 text-sm text-white outline-none focus:border-lime-300"
                    required
                  />
                </label>
              </div>

              <label className="block text-xs text-emerald-50/70">
                Observation date
                <input
                  type="date"
                  value={observationDate}
                  onChange={(event) =>
                    setObservationDate(event.target.value)
                  }
                  className="mt-2 w-full rounded-xl border border-white/10 bg-[#19382b] px-3 py-3 text-sm text-white outline-none focus:border-lime-300"
                  required
                />
              </label>

              <button
                type="submit"
                disabled={loading !== ""}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-lime-400 px-4 py-3 text-sm font-semibold text-[#10251d] transition hover:bg-lime-300 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading === "farm" ? (
                  <LoaderCircle size={17} className="animate-spin" />
                ) : (
                  <ArrowUpRight size={17} />
                )}
                Load farm
              </button>
            </form>
          </div>
        </div>
      </section>

      {error && (
        <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          <AlertCircle size={19} className="mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {notice && !error && (
        <div className="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
          <CheckCircle2 size={19} className="mt-0.5 shrink-0" />
          <span>{notice}</span>
        </div>
      )}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Selected farm"
          value={farm ? farmName : "Not loaded"}
          description={farm ? `Farm ID: ${farmId}` : "Load a farm to view its details"}
          icon={MapPinned}
          accent="green"
        />

        <StatCard
          label="Elevation"
          value={
            elevation.elevation_m != null
              ? `${formatNumber(elevation.elevation_m)} m`
              : "—"
          }
          description="Elevation from the collected farm features"
          icon={MapPin}
          accent="blue"
        />

        <StatCard
          label="Mean NDVI"
          value={formatNumber(ndvi.mean)}
          description={
            ndvi.image_count != null
              ? `${ndvi.image_count} satellite image(s) reported`
              : "Satellite vegetation indicator"
          }
          icon={Sprout}
          accent="lime"
        />

        <StatCard
          label="Predicted yield"
          value={
            predictedYield != null
              ? `${formatNumber(predictedYield)} kg/ha`
              : "Not predicted"
          }
          description="Model estimate for the selected crop cycle"
          icon={TrendingUp}
          accent="amber"
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-2xl border border-stone-200 bg-white p-5 md:p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-stone-900">
                Farm features
              </h2>
              <p className="mt-1 text-sm text-stone-500">
                Weather, vegetation and soil data
              </p>
            </div>

            <button
              type="button"
              onClick={loadFeatures}
              disabled={loading !== ""}
              className="inline-flex items-center gap-2 rounded-xl bg-[#10251d] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#1b3b2c] disabled:opacity-50"
            >
              <RefreshCw
                size={16}
                className={loading === "features" ? "animate-spin" : ""}
              />
              {loading === "features" ? "Collecting..." : "Collect features"}
            </button>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl bg-sky-50/70 p-4">
              <div className="flex items-center gap-2 text-sky-800">
                <CloudRain size={18} />
                <h3 className="font-semibold">Weather</h3>
              </div>
              <DataRow
                label="Rainfall"
                value={
                  weather.rainfall_mm != null
                    ? `${formatNumber(weather.rainfall_mm)} mm`
                    : weather.rainfall_mm === 0
                      ? "0 mm"
                      : "—"
                }
              />
              <DataRow
                label="Temperature"
                value={
                  weather.temperature != null
                    ? `${formatNumber(weather.temperature)} °C`
                    : "—"
                }
              />
            </div>

            <div className="rounded-xl bg-lime-50/70 p-4">
              <div className="flex items-center gap-2 text-lime-800">
                <Sprout size={18} />
                <h3 className="font-semibold">Vegetation</h3>
              </div>
              <DataRow label="Mean NDVI" value={formatNumber(ndvi.mean)} />
              <DataRow label="Minimum NDVI" value={formatNumber(ndvi.min)} />
              <DataRow label="Maximum NDVI" value={formatNumber(ndvi.max)} />
            </div>

            <div className="rounded-xl bg-amber-50/70 p-4 sm:col-span-2">
              <div className="flex items-center gap-2 text-amber-800">
                <Database size={18} />
                <h3 className="font-semibold">Soil characteristics</h3>
              </div>

              <div className="mt-2 grid gap-x-6 sm:grid-cols-2">
                <DataRow label="Soil pH" value={formatNumber(soil.pH)} />
                <DataRow
                  label="Clay"
                  value={
                    soil.soil_clay != null
                      ? formatNumber(soil.soil_clay)
                      : "—"
                  }
                />
                <DataRow
                  label="Organic carbon"
                  value={formatNumber(soil.soil_orgC)}
                />
                <DataRow
                  label="ECEC"
                  value={formatNumber(soil.soil_ECEC)}
                />
                <DataRow
                  label="Root-zone water capacity"
                  value={formatNumber(soil.soil_rzpawhc)}
                />
                <DataRow
                  label="Soil data source"
                  value={soil.source || "—"}
                />
              </div>
            </div>
          </div>

          {features && (
            <div className="mt-4 rounded-xl border border-emerald-100 bg-emerald-50/50 p-3 text-xs text-emerald-800">
              Features received from the API for {observationDate}.
            </div>
          )}
        </div>

        <div className="rounded-2xl border border-stone-200 bg-white p-5 md:p-6">
          <div>
            <h2 className="text-lg font-semibold text-stone-900">
              Maize yield prediction
            </h2>
            <p className="mt-1 text-sm text-stone-500">
              Run the trained model for the selected farm and crop cycle.
            </p>
          </div>

          <div className="mt-5 rounded-2xl bg-[#10251d] p-5 text-white">
            <div className="flex items-center justify-between">
              <span className="text-sm text-emerald-50/70">
                Estimated yield
              </span>
              <TrendingUp size={20} className="text-lime-300" />
            </div>

            <div className="mt-4">
              <span className="text-3xl font-bold tracking-tight">
                {predictedYield != null
                  ? formatNumber(predictedYield)
                  : "—"}
              </span>
              <span className="ml-2 text-sm text-emerald-50/60">kg/ha</span>
            </div>

            <p className="mt-3 text-xs leading-5 text-emerald-50/60">
              This is a model estimate, not a guaranteed harvest outcome.
              Accuracy depends on the quality and suitability of the input data.
            </p>

            <button
              type="button"
              onClick={runPrediction}
              disabled={loading !== ""}
              className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-lime-400 px-4 py-3 text-sm font-semibold text-[#10251d] transition hover:bg-lime-300 disabled:opacity-50"
            >
              {loading === "prediction" ? (
                <LoaderCircle size={17} className="animate-spin" />
              ) : (
                <TrendingUp size={17} />
              )}
              {loading === "prediction"
                ? "Generating prediction..."
                : "Generate yield prediction"}
            </button>
          </div>

          {prediction && (
            <div className="mt-4 space-y-1 rounded-xl border border-stone-200 p-4">
              <DataRow
                label="Prediction ID"
                value={prediction.prediction_id ?? "—"}
              />
              <DataRow
                label="Model version"
                value={prediction.model_version ?? "—"}
              />
              <DataRow
                label="Unit"
                value={prediction.unit ?? "kg/ha"}
              />
              <DataRow
                label="Crop cycle"
                value={prediction.cycle_id ?? cycleId}
              />
            </div>
          )}
        </div>
      </section>

      <section className="rounded-2xl border border-stone-200 bg-white p-5 md:p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-stone-900">
              Prediction history
            </h2>
            <p className="mt-1 text-sm text-stone-500">
              Saved predictions associated with this farm
            </p>
          </div>

          <button
            type="button"
            onClick={loadFarm}
            disabled={loading !== ""}
            className="inline-flex items-center gap-2 rounded-xl border border-stone-200 px-3 py-2 text-sm text-stone-600 hover:bg-stone-50 disabled:opacity-50"
          >
            <RefreshCw size={15} />
            Refresh
          </button>
        </div>

        {history.length > 0 ? (
          <div className="mt-5 overflow-x-auto">
            <table className="w-full min-w-[540px] text-left text-sm">
              <thead>
                <tr className="border-b border-stone-200 text-xs uppercase tracking-wider text-stone-400">
                  <th className="px-3 py-3 font-medium">Prediction ID</th>
                  <th className="px-3 py-3 font-medium">Cycle</th>
                  <th className="px-3 py-3 font-medium">Estimated yield</th>
                  <th className="px-3 py-3 font-medium">Model</th>
                  <th className="px-3 py-3 font-medium">Date</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item, index) => (
                  <tr
                    key={
                      item.prediction_id ??
                      `${item.cycle_id}-${item.prediction_date}-${index}`
                    }
                    className="border-b border-stone-100 last:border-0"
                  >
                    <td className="px-3 py-4 font-medium text-stone-800">
                      {item.prediction_id ?? "—"}
                    </td>
                    <td className="px-3 py-4 text-stone-600">
                      {item.cycle_id ?? "—"}
                    </td>
                    <td className="px-3 py-4 font-semibold text-emerald-800">
                      {item.predicted_yield != null
                        ? `${formatNumber(item.predicted_yield)} kg/ha`
                        : "—"}
                    </td>
                    <td className="px-3 py-4 text-stone-600">
                      {item.model_version ?? "—"}
                    </td>
                    <td className="px-3 py-4 text-stone-600">
                      {item.prediction_date
                        ? String(item.prediction_date).slice(0, 10)
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="mt-5 flex flex-col items-center rounded-2xl border border-dashed border-stone-200 px-5 py-10 text-center">
            <div className="rounded-2xl bg-stone-100 p-3 text-stone-500">
              <CalendarDays size={23} />
            </div>
            <p className="mt-3 font-medium text-stone-800">
              No prediction history loaded
            </p>
            <p className="mt-1 max-w-sm text-sm leading-5 text-stone-500">
              Load a farm to retrieve saved predictions, or generate a new
              prediction for its crop cycle.
            </p>
          </div>
        )}
      </section>

      <footer className="flex flex-wrap items-center justify-between gap-2 pb-2 text-xs text-stone-400">
        <span>Mkulima · Geospatial agricultural decision support</span>
        <span>Weather · Satellite · Soil · Yield modelling</span>
      </footer>
    </div>
  );
}