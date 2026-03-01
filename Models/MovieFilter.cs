namespace MovieApi.Models
{
    public class MovieFilter
    {
        public int? Year { get; set; }
        public string? Genre { get; set; }
        public double? MinRating { get; set; }
        public string? Director { get; set; }
    }
}