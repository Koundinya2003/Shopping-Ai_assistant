import { memo } from "react"
import { StarIcon } from "@heroicons/react/24/solid"

interface RatingProps {
  rating: number
  reviews?: number
  className?: string
}

export const Rating = memo(function Rating({
  rating,
  reviews,
  className = "",
}: RatingProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 text-caption font-semibold ${className}`}
    >
      <StarIcon aria-hidden className="icon-sm text-primary" />
      <span className="text-foreground">{rating.toFixed(1)}</span>
      {reviews != null && (
        <span className="font-medium text-muted-foreground">
          ({reviews.toLocaleString()})
        </span>
      )}
    </span>
  )
})

export default Rating