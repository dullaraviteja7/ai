package com.example.userservice.model;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Min;
import javax.validation.constraints.Size;
import java.util.List;

@Data
@Document(collection = "users")
public class User {
    @Id
    private String id;

    @NotBlank(message = "Name is mandatory")
    private String name;

    @NotNull(message = "Age is mandatory")
    @Min(value = 1, message = "Age must be at least 1")
    private Integer age;

    @NotBlank(message = "Grade is mandatory")
    private String grade;

    @NotNull(message = "Subjects are mandatory")
    @Size(min = 1, message = "At least one subject is required")
    private List<String> subjects;

    private String schoolName;
    private String schoolTimings;
    private String preferredStudyHours;
    private List<String> improvementAreas;
    private List<String> preferredSubjects;
}
