// #region all
interface PropsCardProps {
  title: string;
  body: string;
}

export function PropsCard(props: PropsCardProps) {
  return (
    <article className="question-card">
      <h2>{props.title}</h2>
      <p>{props.body}</p>
    </article>
  );
}
// #endregion all
