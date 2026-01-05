import { Badge } from '@/components/ui/badge';
import type { RunStatus } from '@/types/api';

interface StatusBadgeProps {
  status: RunStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const variantMap: Record<RunStatus, 'default' | 'success' | 'warning' | 'error'> = {
    PENDING: 'default',
    RUNNING: 'warning',
    COMPLETED: 'success',
    FAILED: 'error',
  };

  return (
    <Badge variant={variantMap[status]}>
      {status}
    </Badge>
  );
}
