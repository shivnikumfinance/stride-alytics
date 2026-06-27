import { classNames } from "../../utils";

interface CardProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
  bodyClassName?: string;
  children: React.ReactNode;
}

export function Card({ title, subtitle, actions, className, bodyClassName, children }: CardProps) {
  return (
    <section className={classNames("bg-white rounded-lg shadow-sm border border-gray-200", className)}>
      {(title || actions) && (
        <header className="flex items-start justify-between gap-4 px-5 py-4 border-b border-gray-200">
          <div>
            {title && <h3 className="text-base font-semibold text-gray-900">{title}</h3>}
            {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </header>
      )}
      <div className={classNames("p-5", bodyClassName)}>{children}</div>
    </section>
  );
}
