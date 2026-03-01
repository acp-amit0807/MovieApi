#!/usr/bin/env python3
import os
from tools.github_tools import post_pr_comment

os.environ['GITHUB_TOKEN'] = open('.env').read().split('GITHUB_TOKEN=')[1].split('\n')[0].strip()

review_comment = """## 🔍 Senior Architect Review

### 1️⃣ Design & Architecture

**File:** `Services/MovieService.cs`

**Risk:** Hard-coded seed data mixed with business logic; no repository abstraction; single implementation with no interface.

**Improvement:** Extract `IMovieService` interface and move seed data to a repository or factory:

```csharp
public interface IMovieService
{
    IEnumerable<Movie> GetMovies(MovieFilter filter);
}

public class InMemoryMovieService : IMovieService
{
    private readonly IMovieRepository _repository;
    public InMemoryMovieService(IMovieRepository repository) => // ...
}
```

---

### 2️⃣ Error Handling

**File:** `Controllers/MoviesController.cs`

**Risk:** No model-state validation or exception handling; malformed requests could fail silently or throw 500s.

**Improvement:** Add validation and error catching:

```csharp
[HttpGet]
public IActionResult GetMovies([FromQuery] MovieFilter filter)
{
    if (!ModelState.IsValid)
        return BadRequest(ModelState);
    
    try
    {
        var movies = _movieService.GetMovies(filter);
        return Ok(movies);
    }
    catch (Exception ex)
    {
        // log error
        return StatusCode(500, "An unexpected error occurred");
    }
}
```

---

### 3️⃣ Naming Conventions

✅ **Clear and descriptive** - all names are consistent and self-documenting.  
💡 **Suggestion:** Rename to `InMemoryMovieService` if persisted variants are planned.

---

### 4️⃣ Code Quality

✅ **No magic numbers** (except seed data, acceptable)  
✅ **No hardcoded values** (except routes, acceptable)  
✅ **No dead code**  
✅ **Functions are properly sized**

---

### 5️⃣ Testing

**Risk:** No test coverage detected—regressions undetected.

**Needed:** Add xUnit test project covering:
- ✅ Positive case: valid filter returns expected results
- ✅ Negative case: invalid input produces errors
- ✅ Edge case: empty repository returns empty list  
- ✅ Exception case: repository failure returns 500

Example:
```csharp
[Fact]
public void GetMovies_FilterByYear_ReturnsMatching()
{
    var service = new MovieService();
    var result = service.GetMovies(new MovieFilter { Year = 2010 });
    Assert.Single(result);
    Assert.Equal("Inception", result.First().Title);
}
```

---

## 📊 Summary

| Aspect | Rating |
|--------|--------|
| Design & Architecture | 7/10 |
| Naming & Style | 8/10 |
| Error Handling | 5/10 |
| Code Quality | 7/10 |
| Testing | 2/10 |

**Overall Score: 6.6/10**

**Recommendation: Changes Required**

Before merging:
1. Add validation and exception handling to controller
2. Introduce `IMovieService` interface
3. Add unit tests (positive/negative/edge/exception cases)
4. Ensure consistent nullability annotations

---

Great foundation! Once these improvements are addressed, this will be ready to merge. 🚀"""

try:
    post_pr_comment('acp-amit0807/MovieApi', 1, review_comment)
    print("✅ Review comment posted to PR #1 successfully!")
except Exception as e:
    print(f"Error posting to PR #1: {e}")
