export default function ComingSoon({ title, phase }) {
  return (
    <div className="card">
      <h1 className="text-xl font-semibold">{title}</h1>
      <p className="mt-2 text-slate-500">This page is built in Phase {phase}.</p>
    </div>
  )
}
