import clsx from "clsx";
import type { ComponentPropsWithoutRef } from "react";

type WorkbenchButtonTone = "primary" | "secondary" | "ghost";

export function WorkbenchButton({
  tone = "ghost",
  small = false,
  className,
  ...props
}: ComponentPropsWithoutRef<"button"> & {
  tone?: WorkbenchButtonTone;
  small?: boolean;
}) {
  return (
    <button
      className={clsx(
        "ui-button",
        `ui-button--${tone}`,
        small && "ui-button--small",
        className
      )}
      {...props}
    />
  );
}

export function WorkbenchIconButton({
  tone = "ghost",
  className,
  ...props
}: ComponentPropsWithoutRef<"button"> & {
  tone?: WorkbenchButtonTone;
}) {
  return (
    <button
      className={clsx("ui-button", `ui-button--${tone}`, "ui-icon-button", className)}
      {...props}
    />
  );
}

export function WorkbenchInput({
  className,
  ...props
}: ComponentPropsWithoutRef<"input">) {
  return <input className={clsx("ui-control", className)} {...props} />;
}

export function WorkbenchTextarea({
  className,
  ...props
}: ComponentPropsWithoutRef<"textarea">) {
  return <textarea className={clsx("ui-control", "ui-control--textarea", className)} {...props} />;
}

export function WorkbenchSelect({
  className,
  ...props
}: ComponentPropsWithoutRef<"select">) {
  return <select className={clsx("ui-control", "ui-select", className)} {...props} />;
}
