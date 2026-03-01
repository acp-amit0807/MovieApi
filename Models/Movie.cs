namespace MovieApi.Models
{
    public class Movie
    {
        public int Id { get; set; }
        public string Title { get; set; }
        public int Year { get; set; }
        public string Genre { get; set; }
        public double Rating { get; set; }
        public string Director { get; set; }
    }
}